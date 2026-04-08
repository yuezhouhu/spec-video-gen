"""Generate pipeline overview figure without LaTeX math strings."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import os

os.makedirs("figures", exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 5.5))
ax.set_xlim(0, 14)
ax.set_ylim(0, 5.5)
ax.axis('off')


def box(x, y, w, h, color, text, fontsize=9, tc='white'):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.12',
                       facecolor=color, edgecolor='#333', linewidth=1.3, zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
            fontsize=fontsize, color=tc, fontweight='bold', zorder=4,
            multialignment='center')


def arr(x1, y1, x2, y2, color='#444', lw=1.8):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw), zorder=5)


# ── Column 1: Prompt + Text Encoder ──────────────────────────────────────────
box(0.15, 2.1, 1.5, 1.0, '#5a5a8a', 'Text\nPrompt', fontsize=10)
arr(1.65, 2.6, 2.15, 2.6)
box(2.15, 2.1, 1.5, 1.0, '#5a5a8a', 'Text\nEncoder', fontsize=10)
arr(3.65, 2.6, 4.1, 2.6)

# ── Column 2: Fork to Drafter (top) and Target (bottom) ──────────────────────
# Vertical fork
ax.plot([4.1, 4.1], [1.35, 3.85], color='#555', lw=1.6, zorder=2)
arr(4.1, 3.85, 4.5, 3.85)   # → Drafter
arr(4.1, 1.35, 4.5, 1.35)   # → Target

# Drafter (top)
box(4.5, 3.35, 2.0, 1.0, '#4C72B0', 'Drafter\n(1.3B params)', fontsize=9)
arr(6.5, 3.85, 6.9, 3.85)

# Draft block output
box(6.9, 3.35, 1.6, 1.0, '#4C72B0', 'Draft Block\nx_hat_b', fontsize=9)
arr(8.5, 3.85, 8.9, 3.85)

# VAE Decode
box(8.9, 3.35, 1.3, 1.0, '#7b8ec8', 'VAE\nDecode', fontsize=9)
arr(10.2, 3.85, 10.55, 3.85)

# ImageReward
box(10.55, 3.35, 1.65, 1.0, '#7b8ec8', 'ImageReward\nScorer', fontsize=9)

# ── Router (diamond) ──────────────────────────────────────────────────────────
rx, ry, rd = 12.5, 2.5, 0.65
diamond = Polygon([[rx, ry + rd], [rx + rd * 0.9, ry],
                   [rx, ry - rd], [rx - rd * 0.9, ry]],
                  facecolor='#f0c040', edgecolor='#333', lw=1.3, zorder=3)
ax.add_patch(diamond)
ax.text(rx, ry + 0.08, 'score >=', ha='center', va='center',
        fontsize=8.2, fontweight='bold', zorder=4)
ax.text(rx, ry - 0.22, 'thresh?', ha='center', va='center',
        fontsize=8.2, fontweight='bold', zorder=4)

# ImageReward → router
arr(12.2, 3.85, rx, ry + rd + 0.02, color='gray', lw=1.4)

# Target (bottom)
box(4.5, 0.85, 2.0, 1.0, '#DD8452', 'Target\n(14B params)', fontsize=9)
arr(6.5, 1.35, 6.9, 1.35)
box(6.9, 0.85, 1.6, 1.0, '#DD8452', 'Target Block\nx_star_b', fontsize=9)

# ── Accept path (right from diamond) ─────────────────────────────────────────
box(13.1, 2.1, 0.85, 0.8, '#55A868', 'Accept\nDraft', fontsize=8.5)
arr(rx + rd * 0.9, ry, 13.1, 2.5, color='#55A868', lw=1.8)
ax.text(12.93, 2.72, 'Yes', fontsize=8.5, color='#2a7a3a', fontweight='bold')

# ── Reject path (down from diamond → target) ─────────────────────────────────
# Diamond bottom → target fork
ax.plot([rx, rx, 4.1], [ry - rd, 0.55, 0.55], color='#C44E52', lw=1.8, zorder=2)
arr(4.1, 0.55, 4.1, 0.85, color='#C44E52', lw=1.8)
ax.text(rx + 0.07, ry - rd - 0.22, 'No', fontsize=8.5, color='#c44e52', fontweight='bold')

# ── Force-reject annotation ───────────────────────────────────────────────────
ax.text(4.5, 5.1,
        'Block 0: always use Target (no KV context for Drafter)',
        fontsize=8.5, color='#C44E52', style='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeedd',
                  edgecolor='#C44E52', alpha=0.9))
ax.annotate('', xy=(5.5, 1.85), xytext=(5.5, 4.95),
            arrowprops=dict(arrowstyle='->', color='#C44E52',
                            lw=1.3, linestyle='dashed'))

# ── Adaptive threshold caption ────────────────────────────────────────────────
ax.text(9.5, 0.12,
        u'Adaptive threshold: \u03c4_b = Q_{1-\u03b1_eff}(pool)  '
        u'[\u03b1_eff = \u03b1 \u00d7 B/(B-1),  B=9,  \u03b1=0.72]',
        ha='center', fontsize=8.5, color='#444',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffde0',
                  edgecolor='#aaa', alpha=0.9))

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(7.0, 5.38,
        'RGSD-Video: Reward-Guided Speculative Block Decoding  '
        '(loop: b = 0, 1, ..., B-1)',
        ha='center', fontsize=11, fontweight='bold', color='#222')

plt.savefig('figures/pipeline_overview.pdf', bbox_inches='tight', dpi=150)
plt.savefig('figures/pipeline_overview.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved figures/pipeline_overview.pdf")
