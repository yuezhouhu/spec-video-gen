"""Quality--speed Pareto curve for Table 1.

Plots VisionReward against speedup relative to target-only: the SDVG
threshold sweep and the SDVG-hybrid sweep as curves, the two boundary
baselines as single points. Values are transcribed from Table 1 of the
paper (1003 MovieGenVideoBench prompts, 832x480, seed 42).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter, FixedLocator, NullFormatter

# (speedup, VisionReward), matching Table 1 row for row. Draft-only is left
# out on purpose: at 3.77x it would stretch the axis and flatten the region
# where the two sweeps actually differ.
TARGET = (1.00, 0.0788)
SDVG = [(1.59, 0.0773), (1.69, 0.0764), (1.88, 0.0757), (2.05, 0.0756)]
HYBRID = [(1.88, 0.0772), (1.96, 0.0764), (2.01, 0.0759), (2.11, 0.0751)]

BLUE, ORANGE, DEEP = '#3c78b4', '#e8853c', '#c2601a'

plt.rcParams.update({'font.size': 10, 'axes.edgecolor': '#666666'})
fig, ax = plt.subplots(figsize=(5.6, 3.7))

sx = [p[0] for p in SDVG]
sy = [p[1] for p in SDVG]
hx = [p[0] for p in HYBRID]
hy = [p[1] for p in HYBRID]

ax.plot(sx, sy, marker='o', color=BLUE, lw=1.8, ms=6,
        label='SDVG (threshold sweep)')
ax.plot(hx, hy, marker='s', color=ORANGE, lw=1.8, ms=6,
        label='SDVG-hybrid (threshold sweep)')
ax.axhline(TARGET[1], color=DEEP, ls='--', lw=1.4, dashes=(6, 4),
           zorder=1, label='Target')
ax.text(0.012, TARGET[1] - 0.0004, 'Target', transform=ax.get_yaxis_transform(),
        ha='left', va='top', fontsize=9, color=DEEP)

ax.set_xlabel('Speedup ($\\times$)')
ax.set_xscale('log')
ax.set_xlim(1.4, 2.25)
ax.xaxis.set_major_locator(FixedLocator([1.4, 1.6, 1.8, 2.0, 2.2]))
ax.xaxis.set_major_formatter(FixedFormatter(
    ['1.4', '1.6', '1.8', '2.0', '2.2']))
ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_ylabel('VisionReward $\\uparrow$')
ax.grid(alpha=0.25, lw=0.6)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc='lower left', fontsize=9)

plt.tight_layout()
plt.savefig('figures/quality_speed_tradeoff.pdf', bbox_inches='tight', dpi=200)
plt.savefig('figures/quality_speed_tradeoff.png', bbox_inches='tight', dpi=200)
plt.close()
print('Saved figures/quality_speed_tradeoff.{pdf,png}')
