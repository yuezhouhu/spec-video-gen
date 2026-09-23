# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the paper repository for **"Speculative Decoding for Autoregressive Video Generation"** (SDVG), prepared with the ICLR 2027 template. The project applies speculative decoding to video generation: a 1.3B drafter proposes video blocks, a reward model scores them, and a fixed-threshold router decides whether to accept the draft or regenerate with the 14B target model.

## Commands

### Build the paper PDF
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

### Generate figures
```bash
python gen_teaser.py          # Figure 1, from the frames in figures/teaser_frames/
python gen_pareto.py          # Figure 3, quality--speed curve (values transcribed from Table 1)
python gen_pipeline_svg.py    # Figure 2, compiles figures/pipeline.tex (TikZ) to PDF/SVG/PNG
```

Figures are written to `figures/`.

## Architecture

### Figure generation scripts
- `gen_teaser.py` — Assembles the teaser grid from pre-extracted frames; no data loading.
- `gen_pareto.py` — Plots VisionReward against speedup for the two threshold sweeps.
- `gen_pipeline_svg.py` — Thin build wrapper: pdflatex + dvisvgm + pdftoppm over `figures/pipeline.tex`.

Figure data is transcribed from the evaluation reports rather than read from
them at build time; the Jupyter-style eval JSONs those reports came from live
under `/rscratch/yuezhouhu/` and are not needed to regenerate a figure.

### Algorithm (SDVG)
For each video block (9 blocks total at 832×480):
1. Run drafter (4 denoising steps) to get a candidate block
2. **Block 0**: always force-regenerate with target (ensures scene composition)
3. **Blocks 1–8**: decode draft → score with ImageReward using **min-frame aggregation** (worst frame = detect artifacts)
4. Compare score against **fixed threshold** τ (calibrated offline)
5. Accept → use draft in KV cache; Reject → regenerate with target

Key results: 1.59× speedup vs target-only, 98.1% quality retention (VisionReward 0.0773 vs 0.0788).

### Paper structure
- `main.tex` — Main paper (introduction, background, method, experiments)
- `references.bib` — Bibliography
- `iclr2027_conference.sty` / `.bst` — ICLR 2027 template style and bibliography style
- `fancyhdr.sty` / `natbib.sty` — Support files bundled with the ICLR template (pinned to the template's versions)

### ICLR submission details
- `main.tex` uses `\usepackage{iclr2027_conference,times}`. The document currently compiles in
  **double-blind submission mode**: the header reads "Under review as a conference paper at ICLR
  2027", authors render as "Anonymous authors / Paper under double-blind review", and a line-number
  ruler appears in the left margin.
- Author names are commented out in the `\author{}` block. For the camera-ready version, uncomment
  `\iclrfinalcopy`, restore the author block and the equal-contribution footnote, and uncomment the
  Acknowledgments heading. Do **not** enable `\iclrfinalcopy` for submission.
- The AI use statement (required), Ethics statement, and Reproducibility statement
  (both recommended) sit between the Conclusion and the bibliography, and do not count toward the
  page limit. **Their bodies are still placeholder text** — search for `% TODO` in `main.tex`.
- Page limit: 9 pages of main text, excluding references and the statements above.
- Bibliography entry types must be defined in `iclr2027_conference.bst`; `@software` is not, so
  software/tool citations use `@misc`.
