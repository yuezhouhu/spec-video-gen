"""Generate the SDVG pipeline figure as a clean SVG.

Usage:  python3 gen_pipeline_svg.py
Writes: figures/pipeline.svg  (+ figures/pipeline.pdf / .png via cairosvg)

One pipeline covers both methods. The base SDVG flow is drawn once; the
two SDVG-hybrid mechanisms appear as deltas on that same flow:

  * cascade scoring    -- green dashed callout in the router panel
  * step-level stitch  -- blue segment on the reject path + legend entry

Flat vector style: light fills, dark strokes, no gradients or shadows.
Type is sized for print: the canvas is included at \\linewidth (~14 cm),
so a 22 px label renders at ~6.5 pt.
"""
import os
os.environ.pop("FONTCONFIG_PATH", None)

FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"
BLUE_F, BLUE_S = "#cfe0f3", "#3c78b4"
ORG_F, ORG_S = "#e8964f", "#a85a20"
GRN, RED = "#3f8f56", "#bf3b2b"
PANEL = "#f1f1ef"
NOTE_F, NOTE_S = "#fdf6d8", "#c9a227"
CASC_F, CASC_S = "#e8f1e8", "#3f8f56"
INK, GREY = "#1c1c1c", "#4f4f4f"
T_HEAD, T_TITLE, T_BOX = 26, 32, 34
T_SUB, T_BODY = 25, 22
T_SMALL, T_FORM = 19, 26

parts = []
add = parts.append


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, fill, stroke, rx=8, sw=1.6, dash=False):
    d = ' stroke-dasharray="6,4"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def text(x, y, s, size=T_BODY, weight="normal", fill=INK, anchor="middle",
         style="normal"):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}" '
        f'text-anchor="{anchor}">{esc(s)}</text>')


_FONT_FILES = {
    ("normal", "normal"): "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ("normal", "italic"): "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ("bold", "normal"): "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}
_cache = {}


def _measure(s, weight, style, size):
    from PIL import ImageFont
    k = (weight, style, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(_FONT_FILES.get(k[:2], _FONT_FILES[("normal", "normal")]), int(size))
    return _cache[k].getlength(s)


def rich(xc, y, spans, size=T_BODY, weight="normal", fill=INK):
    total = sum(_measure(t, weight, "italic" if it else "normal", sz or size)
                for t, _, sz, it in spans)
    out = []
    for t, dy, sz, it in spans:
        a = f'dy="{dy}"' if dy else ""
        if sz:
            a += f' font-size="{sz}"'
        if it:
            a += ' font-style="italic"'
        out.append(f"<tspan {a}>{esc(t)}</tspan>")
    add(f'<text x="{xc - total / 2:.1f}" y="{y}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="start">' + "".join(out) + "</text>")


def arrow(x1, y1, x2, y2, color=INK, sw=2.6, dashed=False, marker="arrow"):
    d = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')


def path_arrow(d, color=INK, sw=2.6, dashed=False, marker="arrow"):
    dd = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'
        f'{dd} marker-end="url(#{marker})"/>')


W, H = 1408, 772
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add('<defs>')
for name, col in [("arrow", INK), ("arrowblue", BLUE_S), ("arroworg", ORG_S),
                  ("arrowgrn", GRN), ("arrowred", RED)]:
    add(f'<marker id="{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="5.2" markerHeight="5.2" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{col}"/></marker>')
add('</defs>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')
add('<g transform="translate(0,-40)">')

PANELS = [
    (24, 214, "Input"),
    (228, 520, "Drafter"),
    (534, 818, "VAE +\nReward Router"),
    (832, 1076, "Target\n(reject path)"),
    (1090, 1384, "Output"),
]
PT, PB = 74, 700
for x0, x1, title in PANELS:
    box(x0, PT, x1 - x0, PB - PT, PANEL, PANEL, rx=16, sw=0)
    cx = (x0 + x1) / 2
    for i, ln in enumerate(title.split("\n")):
        text(cx, 110 + i * 42, ln, size=T_TITLE, weight="bold")

# ── input ───────────────────────────────────────────────────────────────────
text(119, 232, "Block", size=T_BODY, fill=GREY)
rich(119, 260, [("b", 0, None, 1), (" = 0, 1, …, 8", 0, None, 1)], size=T_BODY, fill=GREY)
box(36, 470, 168, 118, "#ffffff", "#9a9a9a", rx=8, sw=1.6)
text(120, 506, "Text", size=24, weight="bold")
text(120, 536, "Prompt", size=24, weight="bold")
text(120, 566, "p", size=24, style="italic")

# ── drafter ─────────────────────────────────────────────────────────────────
DBX, DBW = 250, 172
box(DBX, 240, DBW, 232, BLUE_F, BLUE_S, rx=12, sw=2.2)
text(DBX + DBW / 2, 288, "Drafter", size=T_BOX, weight="bold", fill="#1d4e7d")
rich(DBX + DBW / 2, 326, [("D", 0, None, 1), ("  (1.3B)", 0, None, 1)], size=T_SUB, fill="#1d4e7d")
nx, ny = DBX + DBW / 2, 382
nodes = [(nx - 44, ny - 16), (nx - 44, ny + 16), (nx - 9, ny - 28),
         (nx - 9, ny), (nx - 9, ny + 28), (nx + 32, ny - 16), (nx + 32, ny + 16)]
for a, b in [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 5), (3, 6), (4, 5), (4, 6)]:
    add(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="#7fa8cf" stroke-width="1.8"/>')
for x, y in nodes:
    add(f'<circle cx="{x}" cy="{y}" r="7" fill="#ffffff" stroke="{BLUE_S}" stroke-width="2"/>')
text(nx, 442, "4 denoising", size=T_SMALL + 1, fill="#1d4e7d")
text(nx, 466, "steps", size=T_SMALL + 1, fill="#1d4e7d")

arrow(206, 528, 244, 528, color=BLUE_S, marker="arrowblue")
text(233, 486, "noise", size=T_SMALL, fill=GREY)
rich(233, 508, [("z", 0, None, 1), ("b", 5, 14, 1)], size=T_SMALL, fill=GREY)

path_arrow("M 424 300 L 512 300 L 512 232 L 546 232", color=BLUE_S, marker="arrowblue")
text(470, 338, "draft block", size=T_SMALL, fill=GREY)
rich(470, 362, [("x̂", 0, None, 1), ("b", 5, 14, 1)], size=T_BODY, fill=GREY)

for i in range(8):
    shade = "#7fb0dd" if i == 0 else "#bcd6ee"
    add(f'<rect x="{DBX + 6 + i * 20}" y="512" width="18" height="26" rx="3" fill="{shade}" stroke="{BLUE_S}" stroke-width="1.6"/>')
text(nx, 578, "KV Cache", size=T_BODY, fill=GREY)
text(nx, 604, "(Drafter)", size=T_BODY, fill=GREY)

# ── VAE + router panel ──────────────────────────────────────────────────────
cx0 = 588
add(f'<ellipse cx="{cx0}" cy="205" rx="40" ry="12" fill="#f4c79b" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<rect x="{cx0 - 40}" y="205" width="80" height="46" fill="#f0b57f" stroke="none"/>')
add(f'<line x1="{cx0 - 40}" y1="205" x2="{cx0 - 40}" y2="251" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<line x1="{cx0 + 40}" y1="205" x2="{cx0 + 40}" y2="251" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<ellipse cx="{cx0}" cy="251" rx="40" ry="12" fill="#e79a4f" stroke="{ORG_S}" stroke-width="1.8"/>')
text(cx0, 236, "VAE", size=T_BODY, weight="bold", fill="#6b3c12")
text(cx0, 282, "Decode", size=T_BODY, weight="bold", fill="#6b3c12")

# frame strips: solid = scored by default, dashed = cascade proxy (hybrid)
text(690, 186, "F = 12 frames", size=T_SMALL, fill=GREY)
for i in range(3):
    x = 660 + i * 34
    add(f'<rect x="{x}" y="200" width="30" height="48" rx="2" fill="#e4e4e4" stroke="#4a4a4a" stroke-width="1.8"/>')
    add(f'<rect x="{x + 4}" y="208" width="22" height="32" fill="#9aa7b5"/>')
rich(730, 276, [("f", 0, None, 1), ("1", 5, 14, 1), (", f", 0, None, 1), ("2", 5, 14, 1),
                (", …, f", 0, None, 1), ("12", 5, 14, 1)], size=T_BODY, fill=GREY)
arrow(630, 232, 654, 232, color=INK, sw=2.2)

path_arrow("M 710 254 L 710 350", color=INK, sw=2.2)
add('<circle cx="710" cy="388" r="30" fill="#c0392b" stroke="#8f2a20" stroke-width="1.8"/>')
add('<path d="M 698 416 L 684 454 L 710 439 L 736 454 L 722 416 Z" fill="#c0392b" stroke="#8f2a20" stroke-width="1.4"/>')
add('<path d="M 710 370 l 6.5 13 14.5 2.4 -10.5 10 2.5 14.4 -13 -6.8 -13 6.8 2.5 -14.4 -10.5 -10 14.5 -2.4 z" fill="#ffffff"/>')
text(668, 382, "ImageReward", size=T_BODY, weight="bold", fill="#8f2a20", anchor="end")
rich(668, 408, [("R", 0, None, 1)], size=T_BODY, fill="#8f2a20")

rich(690, 512, [("q", 0, None, 1), ("b", 5, 15, 1), (" = min", -5, None, 1),
                ("i", 5, 15, 1), (" R(f", -5, None, 1), ("i", 5, 15, 1),
                (", p)", -5, None, 1)], size=T_FORM)
path_arrow("M 742 388 L 776 388 L 776 330 L 800 330", color=INK)

# block-0 note
box(542, 556, 130, 72, NOTE_F, NOTE_S, rx=10, sw=1.8, dash=True)
text(607, 582, "Block 0:", size=T_SMALL - 2, weight="bold", fill="#7a5c00")
text(607, 601, "force-reject", size=T_SMALL - 2, weight="bold", fill="#7a5c00")
text(607, 620, "(scene anchor)", size=T_SMALL - 2, weight="bold", fill="#7a5c00")

# ── router diamond ──────────────────────────────────────────────────────────
add('<polygon points="866,282 928,340 866,398 804,340" fill="#ffffff" stroke="#8a8a8a" stroke-width="2"/>')
rich(866, 348, [("q", 0, None, 1), ("b", 5, 15, 1), (" ≥ τ", -5, None, 1)], size=T_BODY)

# accept
path_arrow("M 928 340 L 1084 340", color=GRN, sw=4, marker="arrowgrn")
text(985, 312, "Accept", size=T_BODY, weight="bold", fill=GRN)
add(f'<path d="M 1012 318 l 11 15 22 -30" fill="none" stroke="{GRN}" stroke-width="4.5"/>')

# ── reject path: step-level stitching (hybrid) ──────────────────────────────
# orange = target steps, blue = the steps the drafter absorbs in SDVG-hybrid
path_arrow("M 866 398 L 866 418", color=ORG_S, sw=4)
add(f'<line x1="866" y1="418" x2="866" y2="466" stroke="{BLUE_S}" stroke-width="4"/>')
path_arrow("M 866 466 L 866 478", color=BLUE_S, sw=4, marker="arrowblue")
text(898, 416, "Reject", size=T_BODY, weight="bold", fill=RED, anchor="start")
add(f'<path d="M 1042 404 l 26 26 M 1068 404 l -26 26" stroke="{RED}" stroke-width="4.5"/>')

# stitching callout on the reject path
box(962, 428, 46, 28, BLUE_F, BLUE_S, rx=6, sw=1.6)
text(985, 448, "k", size=T_BODY, weight="bold", fill="#1d4e7d")
path_arrow("M 962 464 L 876 464", color=BLUE_S, sw=2.0, marker="arrowblue")

# target box
box(852, 478, 154, 148, ORG_F, ORG_S, rx=12, sw=2.2)
text(929, 518, "Target", size=T_BOX, weight="bold", fill="#ffffff")
rich(929, 552, [("T", 0, None, 1), ("  (14B)", 0, None, 1)], size=T_SUB, fill="#ffffff")
for dy in (0, 13, 26):
    add(f'<path d="M 901 {576 + dy} L 929 {565 + dy} L 957 {576 + dy} L 929 {587 + dy} Z" fill="#ffffff" stroke="{ORG_S}" stroke-width="1.4"/>')
text(929, 616, "steps k…3 in T", size=T_SMALL - 2, fill="#ffffff")

path_arrow("M 1006 548 L 1112 548", color=ORG_S, marker="arroworg")
text(1060, 512, "Regenerated", size=T_SMALL, fill=GREY)
rich(1060, 534, [("block ", 0, None, 0), ("x*", 0, None, 1), ("b", 5, 14, 1)], size=T_SMALL, fill=GREY)

# ── cascade callout (hybrid) ────────────────────────────────────────────────
box(684, 556, 130, 72, CASC_F, CASC_S, rx=10, sw=1.8, dash=True)
text(749, 580, "Cascade", size=T_SMALL - 2, weight="bold", fill="#2f6b40")
text(749, 599, "4 of 12", size=T_SMALL - 2, fill="#2f6b40")
text(749, 618, "frames first", size=T_SMALL - 2, fill="#2f6b40")

# ── output ──────────────────────────────────────────────────────────────────
text(1237, 200, "KV Cache (Target)", size=T_BODY, weight="bold")
add('<rect x="1112" y="232" width="38" height="34" rx="5" fill="#4a4a4a"/>')
add('<path d="M 1120 232 v -9 a 11 11 0 0 1 22 0 v 9" fill="none" stroke="#4a4a4a" stroke-width="4.5"/>')
add('<circle cx="1131" cy="245" r="4.5" fill="#ffffff"/>')
for i in range(4):
    add(f'<rect x="{1160 + i * 30}" y="230" width="28" height="36" rx="3" fill="{"#7fb0dd" if i % 2 == 0 else "#bcd6ee"}" stroke="{BLUE_S}" stroke-width="1.6"/>')
for i in range(3):
    add(f'<rect x="{1160 + (4 + i) * 30}" y="230" width="28" height="36" rx="3" fill="#efb27a" stroke="{ORG_S}" stroke-width="1.6"/>')
for r in range(2):
    for c in range(4):
        x, y = 1134 + c * 50, 330 + r * 68
        add(f'<rect x="{x}" y="{y}" width="46" height="62" rx="3" fill="#5b6b5e" stroke="#2f3a31" stroke-width="2.2"/>')
        add(f'<rect x="{x + 6}" y="{y + 8}" width="34" height="46" fill="#8fa393"/>')
text(1237, 512, "Output Video", size=T_SUB, weight="bold")
text(1237, 544, "(27 frames)", size=T_SUB, weight="bold")

# ── legend ──────────────────────────────────────────────────────────────────
LT = 28
text(64, 716, "LEGEND", size=T_BODY, weight="bold", anchor="start")
box(148, 690, 30, 30, "#5f9fd6", "#3c78b4", rx=6, sw=2)
text(190, 710, "Draft accepted", size=T_SMALL, anchor="start")
box(346, 690, 30, 30, "#e8853c", "#a85a20", rx=6, sw=2)
text(388, 710, "Target regenerated", size=T_SMALL, anchor="start")
box(600, 690, 30, 30, BLUE_F, BLUE_S, rx=6, sw=2)
text(642, 710, "Hybrid: drafter runs steps 0…k−1", size=T_SMALL, anchor="start")
box(966, 690, 30, 30, CASC_F, CASC_S, rx=6, sw=2, dash=True)
text(1008, 710, "Hybrid: 4-frame proxy score", size=T_SMALL, anchor="start")

add('</g>')
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
