"""Generate figures for the NeurIPS 2026 paper."""
import json
import re
import os
import statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

os.makedirs("figures", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Figure 1: VisionReward score distributions (violin + stripplot)
# ─────────────────────────────────────────────────────────────────────────────
def load_scores(path):
    with open(path) as f:
        data = json.load(f)
    return [v['score'] for v in data]

draft_scores  = load_scores('/rscratch/yuezhouhu/VisionReward/eval_draft_only_200.json')
reward_scores = load_scores('/rscratch/yuezhouhu/VisionReward/eval_reward_200.json')
target_scores = load_scores('/rscratch/yuezhouhu/VisionReward/eval_target_only_200.json')

colors = ['#4C72B0', '#DD8452', '#55A868']
labels = ['Draft-only\n(3.07× faster)', 'RGSD (ours)\n(1.66× faster)', 'Target-only\n(baseline)']
all_scores = [draft_scores, reward_scores, target_scores]
means = [statistics.mean(s) for s in all_scores]
stds  = [statistics.stdev(s) for s in all_scores]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

# Left: violin plot
ax = axes[0]
parts = ax.violinplot(all_scores, positions=[1, 2, 3], showmedians=True,
                       showextrema=True, widths=0.7)
for i, (body, color) in enumerate(zip(parts['bodies'], colors)):
    body.set_facecolor(color)
    body.set_alpha(0.75)
for part in ['cmedians', 'cbars', 'cmins', 'cmaxes']:
    parts[part].set_color('black')
    parts[part].set_linewidth(1.5)

# Overlay mean dots
for i, (m, color) in enumerate(zip(means, colors)):
    ax.scatter(i + 1, m, color=color, s=80, zorder=5, edgecolors='black', linewidths=1.2)

ax.set_xticks([1, 2, 3])
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel('VisionReward Score', fontsize=11)
ax.set_title('VisionReward Score Distribution\n(200 prompts, 832×480)', fontsize=10)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_ylim(-0.35, 0.35)
ax.grid(axis='y', alpha=0.3)

# Right: bar chart with error bars
ax2 = axes[1]
x = np.arange(3)
bars = ax2.bar(x, means, yerr=stds, capsize=5, color=colors, alpha=0.85,
               edgecolor='black', linewidth=0.8, error_kw={'linewidth': 1.5})
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=9)
ax2.set_ylabel('VisionReward Score (mean ± std)', fontsize=10)
ax2.set_title('Mean VisionReward Score\nwith Standard Deviation', fontsize=10)

# Annotate bars
for bar, m, s in zip(bars, means, stds):
    ax2.text(bar.get_x() + bar.get_width() / 2, m + s + 0.005,
             f'{m:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2.set_ylim(0, 0.12)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('figures/visionreward_comparison.pdf', bbox_inches='tight', dpi=150)
plt.savefig('figures/visionreward_comparison.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved figures/visionreward_comparison.pdf")

# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: ImageReward score distribution (accepted vs rejected blocks)
# ─────────────────────────────────────────────────────────────────────────────
logfile = '/rscratch/yuezhouhu/realtime-video/logs/reward_200.log'
accepted_scores = []
rejected_scores = []

with open(logfile) as f:
    for line in f:
        m = re.search(
            r'Block (\d+): ImageReward.*?score\(\w+\)=([-\d.]+),.*?accept=(True|False)',
            line
        )
        if m:
            block_idx = int(m.group(1))
            score = float(m.group(2))
            accept = m.group(3) == 'True'
            if accept:
                accepted_scores.append(score)
            else:
                rejected_scores.append(score)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Left: histogram
ax = axes[0]
bins = np.linspace(-2.5, 2.5, 40)
ax.hist(accepted_scores, bins=bins, alpha=0.7, color='#55A868', label=f'Accepted (n={len(accepted_scores)})', density=True)
ax.hist(rejected_scores, bins=bins, alpha=0.7, color='#C44E52', label=f'Rejected (n={len(rejected_scores)})', density=True)
ax.set_xlabel('ImageReward Score (min-frame)', fontsize=11)
ax.set_ylabel('Density', fontsize=11)
ax.set_title('ImageReward Score Distribution\nfor Accepted vs. Rejected Draft Blocks', fontsize=10)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Means
ax.axvline(np.mean(accepted_scores), color='#55A868', linestyle='--', linewidth=2,
           label=f'Mean accepted: {np.mean(accepted_scores):.3f}')
ax.axvline(np.mean(rejected_scores), color='#C44E52', linestyle='--', linewidth=2,
           label=f'Mean rejected: {np.mean(rejected_scores):.3f}')
ax.legend(fontsize=8)

# Right: per-video accept rate
# Parse accept rates per video (blocks 1-8 only)
per_video_accepts = []
cur_acc, cur_total = 0, 0

with open(logfile) as f:
    content = f.read()

video_blocks = re.split(r'Sampling took', content)
for segment in video_blocks[:-1]:  # last segment is after last timing
    accepts = re.findall(r'accept=(True|False)', segment)
    if accepts:
        n_acc = accepts.count('True')
        per_video_accepts.append(n_acc / len(accepts))

ax2 = axes[1]
accept_bins = np.linspace(0, 1.05, 22)
ax2.hist(per_video_accepts, bins=accept_bins, color='#4C72B0', alpha=0.8,
         edgecolor='black', linewidth=0.5)
ax2.axvline(np.mean(per_video_accepts), color='red', linestyle='--', linewidth=2,
            label=f'Mean: {np.mean(per_video_accepts):.2f}')
ax2.axvline(0.72, color='orange', linestyle=':', linewidth=2, label='Target: 0.72')
ax2.set_xlabel('Accept Rate per Video', fontsize=11)
ax2.set_ylabel('Count', fontsize=11)
ax2.set_title(f'Per-Video Accept Rate Distribution\n(n={len(per_video_accepts)} videos)', fontsize=10)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('figures/routing_analysis.pdf', bbox_inches='tight', dpi=150)
plt.savefig('figures/routing_analysis.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved figures/routing_analysis.pdf")

# ─────────────────────────────────────────────────────────────────────────────
# Figure 3: Quality–Speed Pareto curve (fixed-threshold sweep, 1003 prompts)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 3.5))

# Data from 1003-prompt fixed-threshold experiments (total wall-clock minutes)
pareto_data = [
    # (label,        VR,     time_s, marker, size, color)
    ('Draft-only',            0.0644, 25.7, 'o', 80, '#4C72B0'),
    ('RSVG (ours)',           0.0773, 60.9, '*',150, '#DD8452'),
    ('Target-only',           0.0788, 97.0, 'o', 80, '#55A868'),
]

# Connecting line (sorted by time)
p_times  = [d[2] for d in pareto_data]
p_scores = [d[1] for d in pareto_data]
ax.plot(p_times, p_scores, '--', color='gray', alpha=0.5, zorder=1)

# Scatter points (no legend labels — each point has its own annotation)
for label, vr, t, mk, sz, c in pareto_data:
    ax.scatter(t, vr, c=c, s=sz*3, marker=mk, zorder=5,
               edgecolors='black', linewidths=1.0)

# Annotations
ann_offsets = {
    'Draft-only':    (5, 0.0018),
    'RSVG (ours)':   (-8, 0.0018),
    'Target-only':   (-12, -0.0022),
}
for label, vr, t, mk, sz, c in pareto_data:
    off = ann_offsets[label]
    ax.annotate(label, (t, vr), xytext=(t + off[0], vr + off[1]), fontsize=9,
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))

# Speedup annotations
draft_t = pareto_data[0][2]
rsvg_t = pareto_data[1][2]
target_t = pareto_data[2][2]
# RSVG vs Target-only
ax.annotate('', xy=(rsvg_t, 0.0685), xytext=(target_t, 0.0685),
            arrowprops=dict(arrowstyle='<->', color='dimgray', lw=1.5))
ax.text((rsvg_t + target_t) / 2, 0.0675, f'{target_t/rsvg_t:.2f}× speedup',
        ha='center', fontsize=8.5, color='dimgray')
# Draft-only vs Target-only
ax.annotate('', xy=(draft_t, 0.0620), xytext=(target_t, 0.0620),
            arrowprops=dict(arrowstyle='<->', color='dimgray', lw=1.5))
ax.text((draft_t + target_t) / 2, 0.0610, f'{target_t/draft_t:.2f}× speedup',
        ha='center', fontsize=8.5, color='dimgray')

ax.set_xlabel('Average Time per Video (seconds) ↓', fontsize=11)
ax.set_ylabel('VisionReward Score ↑', fontsize=11)
ax.grid(alpha=0.3)
ax.set_xlim(15, 110)
ax.set_ylim(0.058, 0.084)

plt.tight_layout()
plt.savefig('figures/quality_speed_tradeoff.pdf', bbox_inches='tight', dpi=150)
plt.savefig('figures/quality_speed_tradeoff.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved figures/quality_speed_tradeoff.pdf")

print("\nAll figures generated successfully.")
print(f"\nKey stats:")
print(f"  Accepted scores: n={len(accepted_scores)}, mean={np.mean(accepted_scores):.3f}, std={np.std(accepted_scores):.3f}")
print(f"  Rejected scores: n={len(rejected_scores)}, mean={np.mean(rejected_scores):.3f}, std={np.std(rejected_scores):.3f}")
print(f"  Per-video accept rate: mean={np.mean(per_video_accepts):.3f}, std={np.std(per_video_accepts):.3f}")
