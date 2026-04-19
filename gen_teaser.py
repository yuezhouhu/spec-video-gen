"""Generate teaser figure: 3 rows (Draft/RSVG/Target) x 2 columns (2 prompts), 4 frames per cell."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os

figdir = '/rscratch/yuezhouhu/realtime-video.paper/figures/teaser_frames'
outdir = '/rscratch/yuezhouhu/realtime-video.paper/figures'

prompts = ['003', '000']  # Big Sur drone, Tokyo street
methods = ['draft', 'rsvg', 'target']
method_labels = ['Draft-only', 'RSVG (ours)', 'Target-only']
frames = [0, 8, 16, 24]

nrows = len(methods)   # 3: draft, rsvg, target
ncols = len(prompts)   # 2: two videos

fig, axes = plt.subplots(nrows, ncols, figsize=(10, 4.5))

for i, method in enumerate(methods):
    for j, prompt_id in enumerate(prompts):
        # Load and concatenate 4 frames horizontally
        imgs = []
        for f in frames:
            path = os.path.join(figdir, f'{method}_{prompt_id}_f{f}.png')
            img = mpimg.imread(path)
            imgs.append(img)
        # Add thin white separator between frames
        sep = np.ones((imgs[0].shape[0], 2, 3), dtype=imgs[0].dtype)
        strips = []
        for k, img in enumerate(imgs):
            if k > 0:
                strips.append(sep)
            strips.append(img)
        concat = np.concatenate(strips, axis=1)

        ax = axes[i, j]
        ax.imshow(concat)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor('#cccccc')
            spine.set_linewidth(0.5)

        # Row labels on left column only
        if j == 0:
            ax.set_ylabel(method_labels[i], fontsize=9, fontweight='bold',
                          rotation=90, labelpad=8)

# Column titles
prompt_texts = [
    '"Drone view of waves crashing\nalong Big Sur\'s garay point beach..."',
    '"A stylish woman walks down\na Tokyo street..."',
]
for j in range(ncols):
    axes[0, j].set_title(prompt_texts[j], fontsize=9, style='italic', pad=8)

plt.subplots_adjust(wspace=0.03, hspace=0.08, left=0.1)
plt.savefig(os.path.join(outdir, 'teaser.pdf'), bbox_inches='tight', dpi=200, pad_inches=0.15)
plt.savefig(os.path.join(outdir, 'teaser.png'), bbox_inches='tight', dpi=200, pad_inches=0.15)
plt.close()
print('Saved teaser figure')
