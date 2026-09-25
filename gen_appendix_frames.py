"""Generate the appendix qualitative figures: 4 methods x 2 prompts x 4 frames.

Usage: python3 gen_appendix_frames.py
Writes: figures/appendix_qualitative_{1,2}.{pdf,png}

Frames in figures/appendix_frames/ were extracted from the evaluation outputs
at 416x240 with:

  ffmpeg -i <outputs>/prompt_<idx>.mp4 -vf "select=eq(n\\,<f>),scale=416:240" \\
         -vframes 1 figures/appendix_frames/<method>_<idx>_f<f>.png

for frames f in {0, 8, 16, 24} and methods draft (realtime-video.draft),
sdvg (realtime-video, reward_fixed_-0.7), hybrid (realtime-video.hybrid,
hybrid_k3_sb0_t-1.0_casc) and target (realtime-video.target).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os

figdir = '/rscratch/yuezhouhu/realtime-video.paper/figures/appendix_frames'
outdir = '/rscratch/yuezhouhu/realtime-video.paper/figures'

methods = ['draft', 'sdvg', 'hybrid', 'target']
method_labels = ['Draft-only', 'SDVG', 'SDVG-hybrid', 'Target-only']
frames = [0, 8, 16, 24]

FIGS = [
    (1, ['100', '200'], [
        '"An oil painting of a natural forest environment with\ncolorful maple trees and cinematic parallax..."',
        '"A basketball player dunking the ball with flair."']),
    (2, ['400', '800'], [
        '"A tortoise whose body is made of glass, with cracks\nrepaired using kintsugi, walks on black sand..."',
        '"A truck right through a bustling street market,\npassing stalls of vibrant fruits and spices."']),
]

for n, prompt_ids, texts in FIGS:
    fig, axes = plt.subplots(len(methods), len(prompt_ids), figsize=(10, 6.0))
    for i, method in enumerate(methods):
        for j, pid in enumerate(prompt_ids):
            imgs = [mpimg.imread(os.path.join(figdir, f'{method}_{pid}_f{f}.png'))
                    for f in frames]
            sep = np.ones((imgs[0].shape[0], 2, 3), dtype=imgs[0].dtype)
            strips = []
            for k, img in enumerate(imgs):
                if k:
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
            if j == 0:
                ax.set_ylabel(method_labels[i], fontsize=9, fontweight='bold',
                              rotation=90, labelpad=8)

    for j, t in enumerate(texts):
        axes[0, j].set_title(t, fontsize=8, style='italic', pad=8)

    plt.subplots_adjust(wspace=0.03, hspace=0.08, left=0.1)
    for ext in ('pdf', 'png'):
        plt.savefig(os.path.join(outdir, f'appendix_qualitative_{n}.{ext}'),
                    bbox_inches='tight', dpi=200, pad_inches=0.15)
    plt.close()
    print(f'Saved figures/appendix_qualitative_{n}.{{pdf,png}}')
