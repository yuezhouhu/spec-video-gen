"""Publication quality--speed plot for Table 1.

Usage: python3 gen_pareto.py
Requires matplotlib. Writes vector PDF/SVG and a 400-dpi PNG to figures/.

Values are transcribed from Table 1 (1003 MovieGenVideoBench prompts,
832x480, seed 42). The original log-speedup scale and every measured point
are preserved. Target-only is a quality reference; draft-only is off-scale.
"""
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator

# (speedup, VisionReward), matching Table 1 row for row. Draft-only is left
# out on purpose: at 3.77x it would stretch the axis and flatten the region
# where the two sweeps actually differ.
TARGET = (1.00, 0.0788)
SDVG = [(1.59, 0.0773), (1.69, 0.0764), (1.88, 0.0757), (2.05, 0.0756)]
HYBRID = [(1.88, 0.0772), (1.96, 0.0764), (2.01, 0.0759), (2.11, 0.0751)]
THRESHOLDS = [-0.7, -1.0, -1.5, -2.0]

# Match the restrained blue/orange palette of the pipeline figure.
BLUE, ORANGE = '#336BA0', '#B66B2E'
INK, MUTED, RULE = '#243247', '#617083', '#D6DEE7'
OUTPUT = Path(__file__).resolve().parent / 'figures'


def label_thresholds(ax, points, offsets, color):
    """Use point offsets so labels retain their spacing at export size."""
    for (x, y), threshold, (dx, dy, align) in zip(points, THRESHOLDS, offsets):
        ax.annotate(
            rf'${threshold:.1f}$', (x, y), xytext=(dx, dy),
            textcoords='offset points', ha=align, va='center',
            color=color, fontsize=10, annotation_clip=False,
            bbox=dict(facecolor='white', edgecolor='none', pad=0.35),
            zorder=5,
        )


def main():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans'],
        'font.size': 11,
        'mathtext.fontset': 'dejavusans',
        'text.color': INK,
        'axes.labelcolor': INK,
        'xtick.color': MUTED,
        'ytick.color': MUTED,
        'axes.linewidth': 0.7,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'path',
        'savefig.facecolor': 'white',
    })
    fig, ax = plt.subplots(figsize=(5.45, 3.95))
    fig.subplots_adjust(left=0.175, right=0.97, bottom=0.215, top=0.84)

    handles = []
    for points, color, marker, name in [
        (SDVG, BLUE, 'o', 'SDVG'),
        (HYBRID, ORANGE, 's', 'SDVG-hybrid'),
    ]:
        ax.plot(
            *zip(*points), color=color, lw=1.9,
            solid_capstyle='round', zorder=3,
        )
        # Draw every observation above both curves, including the crossing.
        ax.scatter(*zip(*points), color=color, marker=marker, s=6.5**2,
                   edgecolors='white', linewidths=0.8, zorder=4)
        handles.append(Line2D(
            [], [], color=color, lw=1.9, marker=marker, ms=6.5,
            markeredgecolor='white', markeredgewidth=0.8, label=name,
        ))

    ax.axhline(TARGET[1], color=MUTED, lw=1.05, dashes=(4.5, 3.2), zorder=2)
    ax.text(
        1.418, TARGET[1] + 0.00012,
        f'Target-only quality  ({TARGET[1]:.4f})',
        color=MUTED, fontsize=10, ha='left', va='bottom',
    )

    label_thresholds(ax, SDVG,
                     [(-8, 11, 'right'), (-8, -12, 'right'),
                      (-8, -13, 'right'), (7, 8, 'left')], BLUE)
    label_thresholds(ax, HYBRID,
                     [(9, 10, 'left'), (9, 10, 'left'),
                      (-12, 0, 'right'), (8, -8, 'left')], ORANGE)

    # Preserve the original logarithmic horizontal axis, shown explicitly.
    ax.set_xscale('log')
    ax.set_xlim(1.4, 2.25)
    ax.set_ylim(0.07465, 0.07915)
    ax.xaxis.set_major_locator(FixedLocator([1.4, 1.6, 1.8, 2.0, 2.2]))
    ax.xaxis.set_major_formatter(FixedFormatter(['1.4', '1.6', '1.8', '2.0', '2.2']))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator([0.075, 0.076, 0.077, 0.078]))
    ax.yaxis.set_major_formatter(FixedFormatter(['0.075', '0.076', '0.077', '0.078']))
    ax.set_xlabel(r'Speedup over target-only ($\times$)', labelpad=9, fontsize=11)
    ax.set_ylabel(r'VisionReward $\uparrow$', labelpad=10, fontsize=11)
    ax.tick_params(axis='both', labelsize=10, length=3.2, width=0.7, pad=5)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(RULE)
    ax.grid(axis='y', color=RULE, lw=0.65, alpha=0.7)
    ax.set_axisbelow(True)

    ax.legend(
        handles=handles,
        loc='lower left', bbox_to_anchor=(0, 1.08), ncol=2,
        frameon=False, fontsize=10.5, handlelength=2.1,
        handletextpad=0.65, columnspacing=2.1, borderaxespad=0,
    )
    OUTPUT.mkdir(exist_ok=True)
    for extension in ('pdf', 'svg', 'png'):
        destination = OUTPUT / f'quality_speed_tradeoff.{extension}'
        fig.savefig(destination, dpi=400, bbox_inches='tight', pad_inches=0.04)
        print(f'Saved {destination.relative_to(OUTPUT.parent)}')
    plt.close(fig)


if __name__ == '__main__':
    main()
