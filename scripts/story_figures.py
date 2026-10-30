#!/usr/bin/env python3
"""Draw reader-facing line figures from freshly reproduced, frozen evidence.

Optional dependency: requirements-figures.txt. These plots display recorded
header-time differences, not independently measured mining durations.
"""
import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import reproduce

TEXT = '#374151'
COLORS = ('#b6533c', '#098486', '#324c6b')
matplotlib.rcParams['svg.hashsalt'] = 'patoshi-timing-audit-reader-lines-v1'
matplotlib.rcParams['svg.fonttype'] = 'none'


def save(fig, output, name, title, description):
    fig.savefig(output / (name + '.png'), dpi=180, bbox_inches='tight', facecolor='white',
                metadata={'Software': 'Patoshi Timing Audit', 'Title': title,
                          'Description': description})
    fig.savefig(output / (name + '.svg'), bbox_inches='tight', facecolor='white',
                metadata={'Date': None, 'Creator': 'Patoshi Timing Audit',
                          'Title': title, 'Description': description})
    plt.close(fig)


def ecdf(ax, seconds, color, label, limits):
    """All observations contribute before clipping the display window."""
    ordered = sorted(seconds)
    if not ordered:
        raise ValueError('A line requires a nonempty sample')
    before = min(ordered[0] / 60 - 1, limits[0] - 1)
    after = max(ordered[-1] / 60 + 1, limits[1] + 1)
    x = [before] + [value / 60 for value in ordered] + [after]
    y = [0.0] + [100 * (i + 1) / len(ordered) for i in range(len(ordered))] + [100.0]
    ax.step(x, y, where='post', color=color, linewidth=2.1,
            label=f'{label}\nN = {len(ordered):,}')
    return {'cases': len(ordered), 'negative': sum(value < 0 for value in ordered),
            'below_300': sum(value < 300 for value in ordered)}


def axes(fig, limits):
    ax = fig.add_axes([0.09, 0.32, 0.86, 0.40])
    ax.set_xlim(*limits)
    ax.set_ylim(0, 100)
    ax.axvspan(limits[0], 0, color=COLORS[0], alpha=0.055)
    ax.axvline(0, color='#94a3b8', linewidth=0.8)
    ax.axvline(5, color=TEXT, linewidth=1.2, linestyle='--')
    ax.text(5.3, 96, '5 minutes', color=TEXT, fontsize=10, va='top')
    ax.set_xlabel('Recorded timestamp gap (minutes)', fontsize=12, labelpad=10)
    ax.set_ylabel('Share of cases at or below this gap (%)', fontsize=11, labelpad=8)
    ax.set_yticks(range(0, 101, 20))
    ax.tick_params(labelsize=10)
    ax.grid(axis='y', color='#e5e7eb', linewidth=0.7)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color('#cbd5e1')
    return ax


def short_summary(summary):
    return f"{summary['below_300']:,}/{summary['cases']:,} = {100*summary['below_300']/summary['cases']:.2f}%"


def plot_reader_timing(events, output):
    fig = plt.figure(figsize=(13.0, 7.2))
    fig.text(0.055, 0.95, 'The correction changes the whole timing distribution',
             fontsize=19, fontweight='bold', color=TEXT)
    fig.text(0.055, 0.90, 'At any point along the bottom, read upward to see how many cases have a gap that small.',
             fontsize=11, color=TEXT)
    ax = axes(fig, (-5, 30))
    ax.set_xticks(range(-5, 31, 5))
    groups = [('original', 'published_delta', 'Published script'),
              ('timestamp_only', 'child_delta', 'One-line repair'),
              ('stated_rule', 'child_delta', 'Full stated test')]
    summaries = []
    for (mode, field, label), color in zip(groups, COLORS):
        summaries.append(ecdf(ax, [row[field] for row in events[mode]], color, label, (-5, 30)))
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.52, 0.85),
               ncol=3, frameon=False, fontsize=11, handlelength=2.7, columnspacing=3.4)
    fig.text(0.055, 0.20, 'Strictly under 5 minutes:', fontsize=11, fontweight='bold', color=TEXT)
    for x, label, summary, color in zip((0.055, 0.35, 0.66),
                                       ('Published', 'One-line repair', 'Full stated test'), summaries, COLORS):
        fig.text(x, 0.155, f'{label}: {short_summary(summary)}', fontsize=11, color=color)
    fig.text(0.055, 0.10, 'Display window: −5 to 30 minutes. All cases count, including negatives and gaps beyond this window.',
             fontsize=10, color=TEXT)
    fig.text(0.055, 0.065, 'Lines use “at or below”; the reported counts use strict <5 minutes. Each version selects a different sample.',
             fontsize=10, color=TEXT)
    fig.text(0.055, 0.03, 'Published output measures A→C; corrected outputs measure B→C. These are miner-supplied header times.',
             fontsize=10, color=TEXT)
    save(fig, output, 'reader_timing_lines', 'The timing correction changes the full distribution',
         'Every selected case contributes to these empirical cumulative distributions. '
         'The displayed x axis is a zoom in minutes; y is a sample percentage. '
         'The original program emits C-minus-A and corrected versions C-minus-B. '
         'Strict below-five-minute counts include negative values and use differing denominators.')
    return dict(zip((group[0] for group in groups), summaries))


def plot_remaining_structure(pair_rows, output):
    fig = plt.figure(figsize=(13.0, 7.4))
    fig.text(0.055, 0.95, 'Timing structure remains in the supplied groups',
             fontsize=19, fontweight='bold', color=TEXT)
    fig.text(0.055, 0.90, 'A separate question: compare consecutive block pairs across the whole frozen dataset.',
             fontsize=11, color=TEXT)
    ax = axes(fig, (-5, 60))
    ax.set_xticks([-5, 0, 5, 10, 20, 30, 40, 50, 60])
    groups = [('PP', 'Both blocks in published group (P→P)', COLORS[2]),
              ('NN', 'Both outside published group (N→N)', COLORS[1])]
    summaries = []
    for pair, label, color in groups:
        values = [int(row['delta_seconds']) for row in pair_rows if row['label_pair'] == pair]
        summaries.append(ecdf(ax, values, color, label, (-5, 60)))
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.52, 0.85),
               ncol=2, frameon=False, fontsize=11, handlelength=2.7, columnspacing=2.3)
    fig.text(0.055, 0.20, 'Strictly under 5 minutes:', fontsize=11, fontweight='bold', color=TEXT)
    for x, label, summary, color in zip((0.055, 0.51), ('P→P', 'N→N'), summaries, (COLORS[2], COLORS[1])):
        fig.text(x, 0.155, f'{label}: {short_summary(summary)}', fontsize=11, color=color)
    fig.text(0.055, 0.105, 'All 49,999 adjacent pairs are classified; this figure displays PP and NN, with no preceding-gap filter.',
             fontsize=10, color=TEXT)
    fig.text(0.055, 0.07, 'P and N are list membership, not established miner identities. Labels may use related timing or nonce features.',
             fontsize=10, color=TEXT)
    fig.text(0.055, 0.035, 'This is not independent label validation. Display: −5 to 60 minutes; negative and long gaps still count.',
             fontsize=10, color=TEXT)
    save(fig, output, 'remaining_timing_structure', 'Recorded timing structure remains in the supplied groups',
         'Empirical cumulative distributions for all adjacent PP and NN pairs in the frozen heights 0–49999. '
         'This is separate from the fast-PPN timing test; no preceding-gap filter is used. '
         'The zoom window does not remove observations from either denominator. '
         'Differences are recorded header times. The supplied labels are not independently validated by this plot.')
    return dict(zip((group[0] for group in groups), summaries))


def main():
    reproduce(ROOT / 'build')
    events = json.loads((ROOT / 'build/events.json').read_text(encoding='utf-8'))['events']
    with (ROOT / 'build/followup/all_adjacent_pairs.csv').open(encoding='utf-8', newline='') as handle:
        pair_rows = list(csv.DictReader(handle))
    if len(pair_rows) != 49_999:
        raise ValueError('Expected every adjacent pair in the audited range')
    output = ROOT / 'docs/figures'
    output.mkdir(parents=True, exist_ok=True)
    report = {'timing_lines': plot_reader_timing(events, output),
              'remaining_structure': plot_remaining_structure(pair_rows, output)}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
