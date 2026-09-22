"""Generate the SDVG pipeline figure as a clean SVG (two-row layout).

Usage:  python3 gen_pipeline_svg.py
Writes: figures/pipeline.svg  (+ figures/pipeline.pdf / .png via cairosvg)

Two stacked rows share one legend:
  (a) SDVG          -- block-level routing: drafter proposes, the reward
                       router accepts or sends the block to the target.
  (b) SDVG-hybrid   -- the same flow plus step-level stitching on the
                       reject path and on-demand cascade scoring.

Redrawn in a flat, vector style: light fills, dark strokes, no gradients
or drop shadows. Type is sized for print: the canvas is included at
\\linewidth (~14 cm), so a 20 px label renders at ~7 pt.
"""
import os

# PyCharm's remote-dev server points FONTCONFIG_PATH at its own tiny font
# directory, which hides system fonts (text then falls back to Fira Code).
os.environ.pop("FONTCONFIG_PATH", None)

FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"

# palette
BLUE_F, BLUE_S = "#cfe0f3", "#3c78b4"      # drafter / draft
ORG_F, ORG_S = "#e8964f", "#a85a20"        # target / regenerated
GRN = "#3f8f56"                            # accept
RED = "#bf3b2b"                            # reject
PANEL = "#f1f1ef"
NOTE_F, NOTE_S = "#fdf6d8", "#c9a227"      # callout notes
CASC_F, CASC_S = "#e8f1e8", "#3f8f56"      # cascade note
STCH_F, STCH_S = "#fdeee6", "#bf5b2b"      # stitching region
INK = "#1c1c1c"
GREY = "#4f4f4f"

# type scale (px on the 1408-px-wide canvas)
T_TITLE, T_BOX = 24, 20                    # panel title / box title
T_SUB, T_BODY = 17, 16                     # box subtitle / body labels
T_SMALL, T_FORM = 13, 17                   # fine print / score formula

parts = []
add = parts.append


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def box(x, y, w, h, fill, stroke, rx=8, sw=1.6, dash=False):
    d = ' stroke-dasharray="6,4"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def text(x, y, s, size=T_BODY, weight="normal", fill=INK, anchor="middle",
         style="normal", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}" '
        f'text-anchor="{anchor}"{sp}>{esc(s)}</text>')


_FONT_FILES = {
    ("normal", "normal"): "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ("normal", "italic"): "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ("bold", "normal"): "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}
_font_cache = {}


def _measure(s, weight, style, size):
    from PIL import ImageFont
    key = (weight, style, size)
    if key not in _font_cache:
        path = _FONT_FILES.get((weight, style), _FONT_FILES[("normal", "normal")])
        _font_cache[key] = ImageFont.truetype(path, int(round(size)))
    return _font_cache[key].getlength(s)


def rich(x_center, y, spans, size=T_BODY, weight="normal", fill=INK):
    """spans: list of (text, dy, sub-size or None, italic or None).

    cairosvg mis-lays-out `text-anchor="middle"` with tspans (each span is
    re-centered independently), so we center manually: measure the run
    with PIL and emit a start-anchored text. `dy` is cumulative in SVG --
    every span carries an explicit dy, and a subscript (dy=+5) must be
    followed by dy=-5 to restore the baseline.
    """
    total = sum(_measure(t, weight, "italic" if it else "normal", sz or size)
                for t, _, sz, it in spans)
    out = []
    for t, dy, sz, it in spans:
        attrs = f'dy="{dy}"' if dy else ""
        if sz:
            attrs += f' font-size="{sz}"'
        if it:
            attrs += ' font-style="italic"'
        out.append(f"<tspan {attrs}>{esc(t)}</tspan>")
    x0 = x_center - total / 2.0
    add(f'<text x="{x0:.1f}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="start">'
        + "".join(out) + "</text>")


def arrow(x1, y1, x2, y2, color=INK, sw=2.0, dashed=False, marker="arrow"):
    d = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')


def path_arrow(d, color=INK, sw=2.0, dashed=False, marker="arrow"):
    dd = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'
        f'{dd} marker-end="url(#{marker})"/>')


W = 1408
H = 812
ROW_H = 318                                  # panel height per row
ROW_TOP = (48, 400)                          # top y of row (a) and row (b)

add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'width="{W}" height="{H}">')
add('<defs>')
for name, col in [("arrow", INK), ("arrowblue", BLUE_S), ("arroworg", ORG_S),
                  ("arrowgrn", GRN), ("arrowred", RED)]:
    add(f'<marker id="{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{col}"/></marker>')
add('</defs>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')

# horizontal panel bounds, shared by both rows
PANELS = [
    (24, 214, "Input"),
    (246, 520, "Drafter"),
    (552, 812, "VAE +\nReward Router"),
    (844, 1084, "Target\n(reject path)"),
    (1116, 1384, "Output"),
]


def row(y0, mode, label):
    """Draw one pipeline row. mode: 'base' | 'hybrid'."""
    hybrid = mode == "hybrid"

    # ── panel backgrounds + titles ──────────────────────────────────────────
    for x0, x1, title in PANELS:
        box(x0, y0, x1 - x0, ROW_H, PANEL, PANEL, rx=14, sw=0)
        cx = (x0 + x1) / 2
        for i, ln in enumerate(title.split("\n")):
            text(cx, y0 + 34 + i * 30, ln, size=T_TITLE, weight="bold")

    # row tag in the left margin
    tag_y = y0 + ROW_H - 6
    text(18, tag_y, f"({label})", size=T_TITLE, weight="bold", anchor="start")

    # ── Input ───────────────────────────────────────────────────────────────
    text(119, y0 + 96, "Block", size=T_SMALL + 1, fill=GREY)
    rich(119, y0 + 118, [("b", 0, None, 1), (" = 0, 1, …, 8", 0, None, 1)],
         size=T_SMALL + 1, fill=GREY)
    box(46, y0 + 168, 146, 76, "#ffffff", "#9a9a9a", rx=8, sw=1.6)
    text(119, y0 + 196, "Text", size=T_SUB, weight="bold")
    text(119, y0 + 218, "Prompt", size=T_SUB, weight="bold")
    rich(119, y0 + 238, [("p", 0, None, 1)], size=T_SUB)

    # ── Drafter ─────────────────────────────────────────────────────────────
    DBX, DBW = 268, 148
    dbx = DBX + DBW / 2
    box(DBX, y0 + 66, DBW, 158, BLUE_F, BLUE_S, rx=10, sw=2.0)
    text(dbx, y0 + 94, "Drafter", size=T_BOX, weight="bold", fill="#1d4e7d")
    rich(dbx, y0 + 116, [("D", 0, None, 1), ("  (1.3B)", 0, None, 1)],
         size=T_SMALL + 1, fill="#1d4e7d")
    nx, ny = dbx, y0 + 152
    nodes = [(nx - 32, ny - 12), (nx - 32, ny + 12), (nx - 7, ny - 21),
             (nx - 7, ny), (nx - 7, ny + 21), (nx + 24, ny - 12), (nx + 24, ny + 12)]
    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 5), (2, 6),
             (3, 5), (3, 6), (4, 5), (4, 6)]
    for a, b in edges:
        add(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" '
            f'y2="{nodes[b][1]}" stroke="#7fa8cf" stroke-width="1.5"/>')
    for x, y in nodes:
        add(f'<circle cx="{x}" cy="{y}" r="5.2" fill="#ffffff" '
            f'stroke="{BLUE_S}" stroke-width="1.7"/>')
    text(dbx, y0 + 196, "4 denoising", size=T_SMALL, fill="#1d4e7d")
    text(dbx, y0 + 214, "steps", size=T_SMALL, fill="#1d4e7d")

    # noise arrow: prompt -> drafter
    arrow(192, y0 + 238, 258, y0 + 238, color=BLUE_S, marker="arrowblue")
    text(222, y0 + 216, "noise", size=T_SMALL, fill=GREY)
    rich(222, y0 + 236, [("z", 0, None, 1), ("b", 4, 11, 1)], size=T_SMALL, fill=GREY)

    # draft block arrow: drafter -> VAE
    path_arrow(f"M 416 {y0 + 110} L 500 {y0 + 110} L 500 {y0 + 96} L 536 {y0 + 96}",
               color=BLUE_S, marker="arrowblue")
    text(470, y0 + 138, "draft block", size=T_SMALL, fill=GREY)
    rich(470, y0 + 158, [("x̂", 0, None, 1), ("b", 4, 11, 1)], size=T_BODY, fill=GREY)

    # drafter KV cache
    for i in range(8):
        shade = "#7fb0dd" if i == 0 else "#bcd6ee"
        add(f'<rect x="{DBX + 6 + i * 17}" y="{y0 + 258}" width="15" height="22" '
            f'rx="3" fill="{shade}" stroke="{BLUE_S}" stroke-width="1.4"/>')
    text(dbx, y0 + 298, "KV Cache (Drafter)", size=T_SMALL, fill=GREY)

    # ── VAE decode ──────────────────────────────────────────────────────────
    vx, vy = 596, y0 + 88
    add(f'<ellipse cx="{vx}" cy="{vy}" rx="25" ry="8" fill="#f4c79b" '
        f'stroke="{ORG_S}" stroke-width="1.7"/>')
    add(f'<rect x="{vx - 25}" y="{vy}" width="50" height="28" fill="#f0b57f" '
        f'stroke="none"/>')
    add(f'<line x1="{vx - 25}" y1="{vy}" x2="{vx - 25}" y2="{vy + 28}" '
        f'stroke="{ORG_S}" stroke-width="1.7"/>')
    add(f'<line x1="{vx + 25}" y1="{vy}" x2="{vx + 25}" y2="{vy + 28}" '
        f'stroke="{ORG_S}" stroke-width="1.7"/>')
    add(f'<ellipse cx="{vx}" cy="{vy + 28}" rx="25" ry="8" fill="#e79a4f" '
        f'stroke="{ORG_S}" stroke-width="1.7"/>')
    text(vx, y0 + 108, "VAE", size=T_SMALL, weight="bold", fill="#6b3c12")
    text(vx, y0 + 146, "Decode", size=T_SMALL, weight="bold", fill="#6b3c12")

    # ── frame strip: scored frames (4 across the cascade, else 3) ───────────
    fw = 4 if hybrid else 3
    fx0 = 646                                    # left edge of the strip
    for i in range(fw):
        x = fx0 + i * 25
        add(f'<rect x="{x}" y="{y0 + 76}" width="22" height="38" rx="2" '
            f'fill="#e4e4e4" stroke="#4a4a4a" stroke-width="1.6"/>')
        add(f'<rect x="{x + 3}" y="{y0 + 82}" width="16" height="26" '
            f'fill="#9aa7b5"/>')
    strip_cx = fx0 + (fw - 1) * 25 / 2 + 11
    arrow(626, y0 + 96, fx0 - 4, y0 + 96, color=INK, sw=1.8)
    if not hybrid:
        text(strip_cx, y0 + 132, "F = 3 frames", size=T_SMALL, fill=GREY)

    # ── ImageReward badge, fed by the scored frames ─────────────────────────
    path_arrow(f"M {strip_cx} {y0 + 142} L {strip_cx} {y0 + 164}", color=INK,
               sw=1.8)
    bx, by = 698, y0 + 190
    add(f'<circle cx="{bx}" cy="{by}" r="24" fill="#c0392b" '
        f'stroke="#8f2a20" stroke-width="1.7"/>')
    add(f'<path d="M {bx - 12} {by + 24} L {bx - 22} {by + 50} L {bx} {by + 38} '
        f'L {bx + 22} {by + 50} L {bx + 12} {by + 24} Z" fill="#c0392b" '
        f'stroke="#8f2a20" stroke-width="1.3"/>')
    add(f'<path d="M {bx} {by - 15} l 5 10.5 11.5 1.9 -8.3 8 2 11.5 '
        f'-10.2 -5.4 -10.2 5.4 2 -11.5 -8.3 -8 11.5 -1.9 z" fill="#ffffff"/>')
    text(bx, y0 + 258, "ImageReward", size=T_SMALL - 1, weight="bold",
         fill="#8f2a20")

    if hybrid:
        # dashed strip = the full-frame pass, reached only inside the band
        for i in range(3):
            x = 568 + i * 22
            add(f'<rect x="{x}" y="{y0 + 196}" width="20" height="32" rx="2" '
                f'fill="#e4e4e4" stroke="#4a4a4a" stroke-width="1.6" '
                f'stroke-dasharray="4,3"/>')
            add(f'<rect x="{x + 3}" y="{y0 + 201}" width="14" height="22" '
                f'fill="#9aa7b5"/>')
        path_arrow(f"M 620 {y0 + 230} L 640 {y0 + 214}", color=GREY, sw=1.6,
                   dashed=True)
        # band note across the bottom of the panel
        box(556, y0 + 268, 250, 42, CASC_F, CASC_S, rx=8, sw=1.5, dash=True)
        text(681, y0 + 287, "Decide from the 4-frame proxy", size=T_SMALL,
             weight="bold", fill="#2f6b40")
        text(681, y0 + 303, "unless τ−δ < q̂b < τ+δ", size=T_SMALL, fill="#2f6b40")
        score_y = y0 + 266
    else:
        rich(700, y0 + 292, [("q", 0, None, 1), ("b", 4, 11, 1),
                             (" = min", -4, None, 1), ("i", 4, 11, 1),
                             (" R(f", -4, None, 1), ("i", 4, 11, 1),
                             (", p)", -4, None, 1)], size=T_SMALL)
        score_y = y0 + 296

    # ── router diamond ──────────────────────────────────────────────────────
    rx, ry = 952, y0 + 140
    add(f'<polygon points="{rx},{ry - 46} {rx + 52},{ry} {rx},{ry + 46} '
        f'{rx - 52},{ry}" fill="#ffffff" stroke="#8a8a8a" stroke-width="1.8"/>')
    if hybrid:
        rich(rx, ry - 4, [("q̂", 0, None, 1), ("b", 4, 12, 1),
                          (" ≥ τ", -4, None, 1)], size=T_SMALL + 1)
        rich(rx, ry + 16, [("| q", 0, None, 1), ("b", 4, 12, 1),
                           (" ≥ τ", -4, None, 1)], size=T_SMALL + 1)
    else:
        rich(rx, ry + 4, [("q", 0, None, 1), ("b", 4, 12, 1),
                          (" ≥ τ", -4, None, 1)], size=T_BODY)

    # ── router diamond ──────────────────────────────────────────────────────
    rx, ry = 952, y0 + 140
    add(f'<polygon points="{rx},{ry - 46} {rx + 52},{ry} {rx},{ry + 46} '
        f'{rx - 52},{ry}" fill="#ffffff" stroke="#8a8a8a" stroke-width="1.8"/>')
    if hybrid:
        rich(rx, ry - 4, [("q̂", 0, None, 1), ("b", 4, 12, 1),
                          (" ≥ τ", -4, None, 1)], size=T_SMALL + 1)
        rich(rx, ry + 16, [("| q", 0, None, 1), ("b", 4, 12, 1),
                           (" ≥ τ", -4, None, 1)], size=T_SMALL + 1)
    else:
        rich(rx, ry + 4, [("q", 0, None, 1), ("b", 4, 12, 1),
                          (" ≥ τ", -4, None, 1)], size=T_BODY)

    # score -> diamond: travel in the gap between the two panels so the
    # line clears the target box (which sits below the diamond)
    path_arrow(f"M 780 {score_y} L 838 {score_y} L 838 {ry - 16} "
               f"L {rx - 48} {ry - 16}", color=INK, sw=1.8)

    # yes -> accept
    path_arrow(f"M {rx + 54} {ry} L 1108 {ry}", color=GRN, sw=3.2,
               marker="arrowgrn")
    text(1022, ry - 22, "Accept", size=T_SMALL + 1, weight="bold", fill=GRN)
    add(f'<path d="M 1052 {ry - 16} l 9 12 18 -24" fill="none" stroke="{GRN}" '
        f'stroke-width="3.6"/>')

    # no -> target
    path_arrow(f"M {rx} {ry + 46} L {rx} {y0 + 232}", color=RED, sw=3.2,
               marker="arrowred")
    text(958, y0 + 210, "Reject", size=T_SMALL + 1, weight="bold", fill=RED,
         anchor="start")
    add(f'<path d="M 1030 {y0 + 196} l 20 20 M 1050 {y0 + 196} l -20 20" '
        f'stroke="{RED}" stroke-width="3.6"/>')

    # ── target box ──────────────────────────────────────────────────────────
    tx0, ty, tw = 846, y0 + 216, 150
    tcx, tcy = tx0 + tw / 2, ty + 31          # centre of the target box
    box(tx0, ty, tw, 62, ORG_F, ORG_S, rx=10, sw=2.0)
    text(tx0 + 18, ty + 26, "Target", size=T_BOX, weight="bold", fill="#ffffff")
    rich(tx0 + 18, ty + 46, [("T", 0, None, 1), ("  (14B)", 0, None, 1)],
         size=T_SMALL, fill="#ffffff")
    for dy in (0, 11, 22):
        add(f'<path d="M {tx0 + 92} {ty + 22 + dy} L {tx0 + 110} {ty + 13 + dy} '
            f'L {tx0 + 128} {ty + 22 + dy} L {tx0 + 110} {ty + 31 + dy} Z" '
            f'fill="#ffffff" stroke="{ORG_S}" stroke-width="1.2"/>')

    if hybrid:
        # stitch callout: the target starts at step k of the schedule.
        # Sits in the column right of the target box, below the reject arrow.
        text(1030, y0 + 294, "k steps drafter-run", size=T_SMALL - 1,
             weight="bold", fill="#1d4e7d")
        path_arrow(f"M 1024 {y0 + 247} L {tx0 + tw + 2} {y0 + 247}",
                   color=BLUE_S, sw=1.6, marker="arrowblue")

    # regenerated block arrow: leave the target panel through its top wall in
    # the gap right of the reject X, then run right and down to the filmstrip
    path_arrow(f"M 1080 {y0 + 220} L 1090 {y0 + 220} L 1090 {y0 + 300} "
               f"L 1142 {y0 + 300}", color=ORG_S, sw=1.8, marker="arroworg")

    # ── Output ──────────────────────────────────────────────────────────────
    text(1250, y0 + 66, "KV Cache (Target)", size=T_SUB, weight="bold")
    add(f'<rect x="1136" y="{y0 + 84}" width="30" height="26" rx="4" '
        f'fill="#4a4a4a"/>')
    add(f'<path d="M 1142 {y0 + 84} v -7 a 9 9 0 0 1 18 0 v 7" fill="none" '
        f'stroke="#4a4a4a" stroke-width="3.6"/>')
    add(f'<circle cx="1151" cy="{y0 + 95}" r="3.6" fill="#ffffff"/>')
    for i in range(4):
        add(f'<rect x="{1174 + i * 26}" y="{y0 + 82}" width="23" height="30" '
            f'rx="3" fill="{"#7fb0dd" if i % 2 == 0 else "#bcd6ee"}" '
            f'stroke="{BLUE_S}" stroke-width="1.4"/>')
    for i in range(3):
        add(f'<rect x="{1174 + (4 + i) * 26}" y="{y0 + 82}" width="23" '
            f'height="30" rx="3" fill="#efb27a" stroke="{ORG_S}" '
            f'stroke-width="1.4"/>')
    for r in range(2):
        for c in range(4):
            x, y = 1150 + c * 44, y0 + 170 + r * 58
            add(f'<rect x="{x}" y="{y}" width="40" height="52" rx="3" '
                f'fill="#5b6b5e" stroke="#2f3a31" stroke-width="1.9"/>')
            add(f'<rect x="{x + 5}" y="{y + 7}" width="30" height="38" '
                f'fill="#8fa393"/>')
    text(1250, y0 + 296, "Output Video (27 frames)", size=T_SMALL + 1,
         weight="bold")

    # ── block-0 note: routing rule shared by both rows, drawn once ──────────
    if not hybrid:
        box(892, y0 + 286, 182, 26, NOTE_F, NOTE_S, rx=6, sw=1.4, dash=True)
        text(983, y0 + 303, "Block 0: always force-reject", size=T_SMALL - 1,
             weight="bold", fill="#7a5c00")


row(ROW_TOP[0], "base", "a")
row(ROW_TOP[1], "hybrid", "b")

# ── shared legend (bottom) ──────────────────────────────────────────────────
text(56, 756, "LEGEND", size=T_BODY, weight="bold", anchor="start")
box(148, 734, 30, 30, "#5f9fd6", "#3c78b4", rx=6, sw=1.8)
text(190, 754, "Draft accepted", size=T_SMALL + 1, anchor="start")
box(346, 734, 30, 30, "#e8853c", "#a85a20", rx=6, sw=1.8)
text(388, 754, "Target regenerated", size=T_SMALL + 1, anchor="start")
box(600, 734, 30, 30, CASC_F, CASC_S, rx=6, sw=1.8, dash=True)
text(642, 742, "Cascade: 4-frame proxy,", size=T_SMALL + 1, anchor="start")
text(642, 764, "full score in the grey band", size=T_SMALL + 1, anchor="start")
box(918, 734, 30, 30, BLUE_F, BLUE_S, rx=6, sw=1.8)
text(960, 742, "Stitched: first k target steps", size=T_SMALL + 1, anchor="start")
text(960, 764, "run in the drafter", size=T_SMALL + 1, anchor="start")

add('</svg>')

svg = "\n".join(parts) + "\n"
os.makedirs("figures", exist_ok=True)
with open("figures/pipeline.svg", "w") as f:
    f.write(svg)
print("Saved figures/pipeline.svg")

try:
    import cairosvg
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to="figures/pipeline.pdf")
    cairosvg.svg2png(bytestring=svg.encode(), write_to="figures/pipeline.png",
                     output_width=W * 2)
    print("Saved figures/pipeline.pdf and figures/pipeline.png")
except Exception as e:  # pragma: no cover
    print(f"cairosvg unavailable ({e}); SVG written but not rasterized")
