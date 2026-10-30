#!/usr/bin/env python3
"""Build exact publication graphics from freshly reproduced counts; matplotlib only."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.hashsalt'] = 'patoshi-timing-audit'
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reproduce import reproduce
counts=reproduce(ROOT/'build')['counts']
BG='#101b2c';WHITE='#f2f5fa';MUTED='#aebbd0';GOLD='#ffb454';TEAL='#66dacd'
fig=plt.figure(figsize=(12,6.3),dpi=160,facecolor=BG)
fig.text(.055,.9,'BITCOIN  /  REPRODUCIBLE RESEARCH',color=GOLD,size=12,weight='bold')
fig.text(.055,.79,'Patoshi Timing Audit',color=WHITE,size=34,weight='bold')
fig.text(.055,.715,'A correction to the 2022 three-block timing test',color=MUTED,size=16)
ax=fig.add_axes([.37,.26,.58,.34],facecolor=BG)
keys=['original','timestamp_only','stated_rule'];colors=[MUTED,TEAL,GOLD]
labels=['Published program','Timestamp repaired','Stated rule']
for y,(k,c,label) in enumerate(zip(keys,colors,labels)):
 r=counts[k];rate=r['less_300']/r['n']*100
 ax.barh(y,rate,color=c,height=.43)
 ax.text(-1.3,y,label,ha='right',va='center',color=WHITE,size=13)
 ax.text(rate+1,y,f'{rate:.2f}%',va='center',color=c,size=15,weight='bold')
 ax.text(57,y,f"{r['less_300']:,} / {r['n']:,}",ha='right',va='center',color=MUTED,size=12)
ax.set_xlim(0,58);ax.set_ylim(2.6,-.7);ax.axis('off')
fig.text(.055,.19,'Share of selected cases with a reported gap below 300 seconds',color=WHITE,size=12)
fig.text(.055,.135,'Each version selects a different sample. Negative gaps are included.',color=MUTED,size=10)
fig.text(.055,.095,'Header timestamps do not establish elapsed mining times or miner identity.',color=MUTED,size=10)
fig.text(.055,.035,'ZAKK EASTERBROOK',color=GOLD,size=10,weight='bold')
fig.text(.95,.035,'50,000 headers  /  Fixed labels  /  Complete outputs',color=MUTED,size=9,ha='right')
out=ROOT/'docs/figures';out.mkdir(parents=True,exist_ok=True)
fig.savefig(out/'release-cover.png',facecolor=BG,dpi=160)
fig.savefig(out/'release-cover.svg',facecolor=BG,metadata={'Date': None})
plt.close(fig)
print('Wrote release cover PNG and SVG from reproduced counts.')
