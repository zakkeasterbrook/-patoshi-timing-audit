#!/usr/bin/env python3
"""Generate publication figures from fresh audit outputs; requires matplotlib."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import reproduce
from inputs import load_inputs

VERSIONS = ["original", "timestamp_only", "stated_rule"]
NAMES = ["Published implementation", "One timestamp assignment repaired", "Stated sequence rule implemented"]
LINE_COLORS = ["#b6533c", "#098486", "#324c6b"]
TEXT = "#374151"

# Stable SVG element IDs and metadata keep repeated regeneration comparable.
matplotlib.rcParams["svg.hashsalt"] = "patoshi-timing-audit-v1"
matplotlib.rcParams["svg.fonttype"] = "none"


def save_figure(fig, output, basename, title, description):
    fig.savefig(output / (basename + ".png"), dpi=180, bbox_inches="tight", facecolor="white",
                metadata={"Software": "Patoshi Timing Audit", "Title": title, "Description": description})
    fig.savefig(output / (basename + ".svg"), bbox_inches="tight", facecolor="white",
                metadata={"Date": None, "Creator": "Patoshi Timing Audit", "Title": title,
                          "Description": description})
    plt.close(fig)


def plot_comparison(counts, output):
    """Preserve the release's original stacked-proportion comparison."""
    colors = ["#b6533c", "#098486", "#d9e1ea"]
    fig, ax = plt.subplots(figsize=(12.8, 4.7))
    for y, version in enumerate(VERSIONS):
        row = counts[version]
        n, negative, below = row["n"], row["negative"], row["less_300"]
        segments = [negative, below - negative, n - below]
        left = 0
        for value, color in zip(segments, colors):
            width = 100 * value / n
            ax.barh(y, width, left=left, height=0.48, color=color)
            left += width
        ax.text(101, y, f"{below:,}/{n:,} below 300 s\n({100*below/n:.2f}%)", va="center", fontsize=11, color="#374151")
    ax.set_yticks(range(3), [f"{name}\nN = {counts[v]['n']:,}" for name, v in zip(NAMES, VERSIONS)])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of the selected cases (%)", fontsize=12)
    ax.tick_params(axis="y", length=0, pad=12, labelsize=11)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.set_title("The corrected timing statistic changes substantially", loc="left", fontsize=16, fontweight="bold", pad=28)
    ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(colors, ["Negative", "0 to <300 seconds", "300 seconds or more"])],
              loc="upper left", bbox_to_anchor=(-0.01, -0.2), ncol=3, frameon=False, fontsize=10)
    fig.subplots_adjust(left=0.35, right=0.81, top=0.80, bottom=0.25)
    fig.text(0.35, 0.015, "Original fixed P labels. Below-300 counts include negatives; sample denominators differ.",
             color=TEXT, fontsize=9)
    save_figure(fig, output, "timing_test_comparison", "The corrected timing statistic changes substantially",
                "Computed selected-case proportions. Original fixed labels; negative timestamp gaps are included.")


def plot_same_sample(events, output):
    """Isolate the measured interval while retaining every legacy-selected case."""
    rows = events["original"]
    if not rows:
        raise ValueError("The fixed-sample diagnostic requires original selected cases")
    n = len(rows)
    specifications = [
        ("Published interval: C − A", "published_delta"),
        ("Intended interval: C − B", "child_delta"),
    ]
    colors = ["#b6533c", "#098486", "#d9e1ea"]
    summaries = []
    fig, ax = plt.subplots(figsize=(12.8, 5.0))
    for y, (name, key) in enumerate(specifications):
        values = [row[key] for row in rows]
        negative = sum(value < 0 for value in values)
        below = sum(value < 300 for value in values)
        summaries.append((negative, below))
        left = 0
        for count, color in zip((negative, below-negative, n-below), colors):
            width = 100 * count / n
            ax.barh(y, width, left=left, height=0.43, color=color)
            left += width
        ax.text(101, y, f"{below:,}/{n:,} below 300 s\n{100*below/n:.2f}% · {negative:,} negative",
                va="center", fontsize=11, color=TEXT)
    ax.set_yticks(range(2), [f"{name}\nN = {n:,}" for name, _ in specifications])
    ax.set_xlim(0, 100)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlabel("Share of the same original selected cases (%)", fontsize=11)
    ax.tick_params(axis="y", length=0, pad=12, labelsize=11)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    fig.subplots_adjust(left=0.30, right=0.79, top=0.74, bottom=0.33)
    fig.text(0.035, 0.94, "Hold the sample fixed: correct the measured interval",
             fontsize=18, fontweight="bold", color=TEXT)
    fig.text(0.035, 0.865,
             f"Both rows use all {n:,} original cases. Only the reported timestamp difference changes.",
             fontsize=11, color=TEXT)
    fig.legend(handles=[Patch(color=color, label=label) for color, label in zip(colors,
               ["Negative", "0 to <300 seconds", "300 seconds or more"])],
               loc="lower left", bbox_to_anchor=(0.29, 0.16), ncol=3,
               frameon=False, fontsize=9.5)
    fig.text(0.035, 0.10,
             "Below-300 counts include negatives. Original selection and eligibility are retained in both rows.",
             fontsize=10, color=TEXT)
    fig.text(0.035, 0.045,
             "This diagnostic isolates the interval error; it is separate from the fully implemented stated test.",
             fontsize=10, color=TEXT)
    save_figure(fig, output, "same_sample_comparison", "The measured interval changes the result on the same cases",
                f"Every one of the {n} original selected cases is retained. Published C-minus-A has "
                f"{summaries[0][1]} differences below 300 seconds; intended C-minus-B has {summaries[1][1]}, "
                f"including {summaries[1][0]} negatives. Legacy selection and eligibility remain unchanged.")


def plot_interval_example(records, labels, output):
    heights = [263, 264, 265]
    timestamps = [records[h]["timestamp"] for h in heights]
    ab, bc, ac = timestamps[1]-timestamps[0], timestamps[2]-timestamps[1], timestamps[2]-timestamps[0]
    classifications = ["P" if h in labels else "N" for h in heights]
    fig = plt.figure(figsize=(12.8, 5.7))
    fig.text(0.05, 0.94, f"The 263–265 example: {bc:,} seconds becomes {ac:,} seconds",
             fontsize=19, fontweight="bold", color=TEXT)
    fig.text(0.05, 0.875, "Header timestamps, Bitcoin mainnet. Block positions below are schematic, not to scale.",
             fontsize=11, color=TEXT)
    ax = fig.add_axes([0.05, 0.18, 0.90, 0.64])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    xs = [0.10, 0.50, 0.90]
    for letter, height, label, timestamp, x in zip("ABC", heights, classifications, timestamps, xs):
        instant = datetime.fromtimestamp(timestamp, timezone.utc)
        color = LINE_COLORS[1] if label == "P" else LINE_COLORS[2]
        ax.text(x, 0.95, f"{letter} · block {height} · {label}", ha="center", va="top", fontsize=13,
                fontweight="bold", color=color)
        ax.text(x, 0.84, instant.strftime("%Y-%m-%d\n%H:%M:%S UTC"), ha="center", va="top", fontsize=12,
                linespacing=1.6, color=TEXT)
        ax.plot(x, 0.59, "o", markersize=9, color=color)
        ax.plot([x, x], [0.15, 0.56], color="#d9e1ea", linewidth=1, linestyle=":")
    arrow_specs = [
        (xs[0], xs[1], 0.43, f"Eligibility: tB − tA = {ab:,} s < 600 s", LINE_COLORS[2]),
        (xs[1], xs[2], 0.43, f"Intended: tC − tB = {bc:,} s", LINE_COLORS[1]),
        (xs[0], xs[2], 0.15, f"Published: tC − tA = {ac:,} s", LINE_COLORS[0]),
    ]
    for start, end, y, text, color in arrow_specs:
        ax.annotate("", xy=(end, y), xytext=(start, y),
                    arrowprops={"arrowstyle": "<->", "color": color, "linewidth": 2})
        ax.text((start+end)/2, y+0.065, text, ha="center", va="bottom", fontsize=12,
                fontweight="bold", color=color)
    fig.text(0.05, 0.12, f"{ab:,} s + {bc:,} s = {ac:,} s. The published assignment reads B’s time from A’s response.",
             fontsize=12, color=TEXT)
    fig.text(0.05, 0.065, "P = in the original frozen label list; N = absent. Header-time differences are not measured elapsed mining times.",
             fontsize=10, color=TEXT)
    save_figure(fig, output, "interval_example", "The block 263–265 timestamp-assignment example",
                "UTC timestamps and interval arithmetic extracted from verified frozen headers; original fixed labels. Schematic spacing.")


def plot_distributions(events, counts, output):
    values = {}
    for version in VERSIONS:
        delta_key = "published_delta" if version == "original" else "child_delta"
        values[version] = sorted(row[delta_key] for row in events[version])
    minimum = min(min(rows) for rows in values.values())
    maximum = max(max(rows) for rows in values.values())
    padding = (maximum-minimum)*0.03
    full_limits = (minimum-padding, maximum+padding)
    fig = plt.figure(figsize=(13.2, 8.2))
    fig.text(0.05, 0.955, "Distributions of reported header-timestamp differences", fontsize=19,
             fontweight="bold", color=TEXT)
    fig.text(0.05, 0.91, "Published program: tC − tA. Corrected versions: tC − tB. Each version selects a different sample.",
             fontsize=11, color=TEXT)
    axes = [fig.add_axes([0.08, 0.43, 0.39, 0.35]), fig.add_axes([0.56, 0.43, 0.39, 0.35])]
    for ax in axes:
        for version, color, name in zip(VERSIONS, LINE_COLORS, NAMES):
            rows = values[version]
            # All observations, including negatives and long tails, contribute
            # to both panels. The second panel clips only the displayed x axis.
            x = [full_limits[0]] + rows + [full_limits[1]]
            y = [0.0] + [(i+1)/len(rows) for i in range(len(rows))] + [1.0]
            ax.step(x, y, where="post", color=color, linewidth=1.7,
                    label=f"{name}\nN = {len(rows):,}")
        ax.axvspan(full_limits[0], 0, color="#b6533c", alpha=0.055, zorder=-1)
        ax.axvline(0, color="#94a3b8", linewidth=0.8)
        ax.axvline(300, color=TEXT, linewidth=1.1, linestyle="--")
        ax.set_ylim(0, 1.025)
        ax.set_xlabel("Reported timestamp difference, d (seconds)", fontsize=10, labelpad=8)
        ax.set_ylabel("Cumulative fraction with difference ≤ d", fontsize=10)
        ax.tick_params(labelsize=9)
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.7)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#cbd5e1")
    axes[0].set_xlim(*full_limits)
    axes[0].set_title(f"Full observed range: {minimum:,} to {maximum:,} s", fontsize=11, loc="left", pad=10)
    axes[0].ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[1].set_xlim(-300, 1800)
    axes[1].set_title("Display zoom: −300 to 1,800 s; full-sample denominators", fontsize=11, loc="left", pad=10)
    axes[1].set_xticks([-300, 0, 300, 600, 900, 1200, 1500, 1800])
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(0.52, 0.875), ncol=3,
               fontsize=10, frameon=False, handlelength=2.5, columnspacing=2.5)
    headings = [(0.08, "Calculation"), (0.52, "Selected cases"), (0.67, "Negative"), (0.79, "d < 300 s"), (0.92, "Rate")]
    for x, label in headings:
        fig.text(x, 0.325, label, fontsize=10, color=TEXT, fontweight="bold", ha="left" if x == 0.08 else "right")
    for y, version, name, color in zip([0.285, 0.245, 0.205], VERSIONS, NAMES, LINE_COLORS):
        row = counts[version]
        fig.text(0.08, y, name, fontsize=11, color=color)
        for x, text in [(0.52, f"{row['n']:,}"), (0.67, f"{row['negative']:,}"),
                        (0.79, f"{row['less_300']:,}"), (0.92, f"{100*row['less_300']/row['n']:.2f}%")]:
            fig.text(x, y, text, fontsize=11, color=TEXT, ha="right")
    fig.text(0.08, 0.135, "Negative differences remain in both ECDFs and in the d < 300 s counts. Dashed line: 300 s.",
             fontsize=10, color=TEXT)
    fig.text(0.08, 0.095, "The ECDF uses ≤ d; the table uses strict < 300 s and excludes values equal to 300. The right panel is a display zoom only.",
             fontsize=9.5, color=TEXT)
    fig.text(0.08, 0.055, "Frozen labels: P = in the original 21,953-height list; N = absent. Audit range: mainnet heights 0–49,999 inclusive.",
             fontsize=9.5, color=TEXT)
    fig.text(0.08, 0.02, "Header-time differences do not independently measure elapsed mining times or identify miners.", fontsize=9.5, color=TEXT)
    save_figure(fig, output, "timing_gap_distributions", "Full empirical distributions of the three timing calculations",
                "ECDFs generated from every freshly reproduced selected case, including negatives. Full range plus explicitly disclosed display zoom; fixed original labels.")


def main():
    counts = reproduce(ROOT / "build")["counts"]
    result = json.loads((ROOT / "build/events.json").read_text(encoding="utf-8"))
    records, labels, _, _ = load_inputs()
    output = ROOT / "docs/figures"
    output.mkdir(parents=True, exist_ok=True)
    plot_comparison(counts, output)
    plot_same_sample(result["events"], output)
    plot_interval_example(records, labels, output)
    plot_distributions(result["events"], counts, output)
    print("Wrote PNG and SVG comparison, fixed-sample, interval and distribution figures from freshly reproduced data.")


if __name__ == "__main__":
    main()
