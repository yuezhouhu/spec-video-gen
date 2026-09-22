"""Generate the SDVG pipeline figure as a clean SVG.

Usage:  python3 gen_pipeline_svg.py
Writes: figures/pipeline.svg  (+ figures/pipeline.pdf / .png via cairosvg)

One pipeline covers both methods. The base SDVG flow is drawn once; the
two SDVG-hybrid mechanisms appear as deltas on that same flow:

  * cascade scoring    -- two frame rows in the router panel: the 4-frame
                          proxy, and the fall-back to all 12 frames
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


def rich(xc, y, spans, size=T_BODY, weight="normal", fill=INK, anchor="middle"):
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
    x = xc - total / 2 if anchor == "middle" else xc - total
    add(f'<text x="{x:.1f}" y="{y}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="start">' + "".join(out) + "</text>")


def arrow(x1, y1, x2, y2, color=INK, sw=2.6, dashed=False, marker="arrow"):
    d = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')


def padlock(x, y, w=16, h=11):
    """Lock body of w x h at (x, y), with its shackle and keyhole above it."""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="#4a4a4a"/>')
    add(f'<path d="M {x + w * 0.19:.1f} {y} a {w * 0.3125:.2f} {w * 0.3125:.2f} '
        f'0 0 1 {w * 0.625:.1f} 0" fill="none" stroke="#4a4a4a" '
        f'stroke-width="2.4"/>')
    add(f'<circle cx="{x + w / 2:.1f}" cy="{y + h * 0.45:.1f}" r="2" '
        f'fill="#ffffff"/>')


def path_arrow(d, color=INK, sw=2.6, dashed=False, marker="arrow"):
    dd = ' stroke-dasharray="6,4"' if dashed else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"'
        f'{dd} marker-end="url(#{marker})"/>')


W, H = 1408, 724
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

# ── input: text prompt + the blocks generated so far ────────────────────────
box(68, 224, 104, 88, "#ffffff", "#9a9a9a", rx=8, sw=1.6)
text(120, 260, "Text", size=T_BODY, weight="bold")
text(120, 284, "Prompt", size=T_BODY, weight="bold")
rich(120, 306, [("p", 0, None, 1)], size=T_BODY)

# generated blocks: block b conditions on blocks 0..b-1. Block 0 always comes
# from the target and is locked in as the scene anchor; the strip is the output
# strip one block short, drawn in the same style
text(119, 460, "generated blocks", size=T_SMALL - 1, fill=GREY)
BW, BP, BH, GY = 24, 26, 32, 474
gx = 119 - (5 * BP + BW) / 2
for i, (fill, stroke) in enumerate([
        ("#efb27a", ORG_S), ("#7fb0dd", BLUE_S), ("#7fb0dd", BLUE_S),
        ("#7fb0dd", BLUE_S), ("#efb27a", ORG_S), ("#7fb0dd", BLUE_S)]):
    add(f'<rect x="{gx + i * BP}" y="{GY}" width="{BW}" height="{BH}" rx="3" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')

# padlock inside block 0: it is the target's own block, never a draft
padlock(gx + BW / 2 - 8, GY + 13)
rich(119, 540, [("0 … b−1", 0, None, 1)], size=T_SMALL, fill=GREY)

# ── drafter ─────────────────────────────────────────────────────────────────
DBX, DBW = 250, 172
DCX = DBX + DBW / 2

# the network icon and the model label sit between the panel title and the
# model box, not inside it
nx, ny = DCX + 6, 230   # the graph is 12 px wider on the left than on the right
nodes = [(nx - 44, ny - 16), (nx - 44, ny + 16), (nx - 9, ny - 28),
         (nx - 9, ny), (nx - 9, ny + 28), (nx + 32, ny - 16), (nx + 32, ny + 16)]
for a, b in [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 5), (3, 6), (4, 5), (4, 6)]:
    add(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="#7fa8cf" stroke-width="1.8"/>')
for x, y in nodes:
    add(f'<circle cx="{x}" cy="{y}" r="7" fill="#ffffff" stroke="{BLUE_S}" stroke-width="2"/>')
rich(DCX, 340, [("D", 0, None, 1), ("  (1.3B)", 0, None, 1)], size=T_SUB, fill="#1d4e7d")

# the four denoising steps: five latent states, light to dark, the last one
# shaded like the draft blocks it produces
SBW, SBH, SBG = 84, 30, 26
sx, sy = DCX - SBW / 2, 390
SHADES = ["#e9f3fc", "#cee2f4", "#b4d2ec", "#99c1e4", "#7fb0dd"]
for i, fill in enumerate(SHADES):
    y = sy + i * (SBH + SBG)
    box(sx, y, SBW, SBH, fill, BLUE_S, rx=6, sw=1.8)
    if i < 4:
        arrow(DCX, y + SBH, DCX, y + SBH + SBG, color=BLUE_S, sw=2.2,
              marker="arrowblue")
text(sx - 12, sy + 22, "Drafter", size=T_SMALL + 1,
     fill=GREY, anchor="end")


path_arrow("M 418 629 L 512 629 L 512 232 L 546 232", color=BLUE_S, marker="arrowblue")
text(462, 338, "draft block", size=T_SMALL, fill=GREY)
rich(462, 362, [("x̂", 0, None, 1), ("b", 5, 14, 1)], size=T_BODY, fill=GREY)


# ── VAE + router panel ──────────────────────────────────────────────────────
cx0 = 588
add(f'<ellipse cx="{cx0}" cy="205" rx="40" ry="12" fill="#f4c79b" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<rect x="{cx0 - 40}" y="205" width="80" height="46" fill="#f0b57f" stroke="none"/>')
add(f'<line x1="{cx0 - 40}" y1="205" x2="{cx0 - 40}" y2="251" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<line x1="{cx0 + 40}" y1="205" x2="{cx0 + 40}" y2="251" stroke="{ORG_S}" stroke-width="1.8"/>')
add(f'<ellipse cx="{cx0}" cy="251" rx="40" ry="12" fill="#e79a4f" stroke="{ORG_S}" stroke-width="1.8"/>')
text(cx0, 236, "VAE", size=T_BODY, weight="bold", fill="#6b3c12")
text(cx0, 282, "Decode", size=T_BODY, weight="bold", fill="#6b3c12")

# the twelve frames of one block; three are drawn
text(690, 186, "F = 12 frames", size=T_SMALL, fill=GREY)
for i in range(3):
    x = 660 + i * 34
    add(f'<rect x="{x}" y="200" width="30" height="48" rx="2" fill="#e4e4e4" stroke="#4a4a4a" stroke-width="1.8"/>')
    add(f'<rect x="{x + 4}" y="208" width="22" height="32" fill="#9aa7b5"/>')
rich(730, 276, [("f", 0, None, 1), ("1", 5, 14, 1), (", f", 0, None, 1), ("2", 5, 14, 1),
                (", …, f", 0, None, 1), ("12", 5, 14, 1)], size=T_BODY, fill=GREY)
arrow(630, 232, 654, 232, color=INK, sw=2.2)

path_arrow("M 710 254 L 710 350", color=INK, sw=2.2)
# the rosette's star, reused at half scale as the cascade proxy badge
STAR = ("M 710 370 l 6.5 13 14.5 2.4 -10.5 10 2.5 14.4 -13 -6.8 -13 6.8 "
        "2.5 -14.4 -10.5 -10 14.5 -2.4 z")
add('<circle cx="710" cy="388" r="30" fill="#c0392b" stroke="#8f2a20" stroke-width="1.8"/>')
add('<path d="M 698 416 L 684 454 L 710 439 L 736 454 L 722 416 Z" fill="#c0392b" stroke="#8f2a20" stroke-width="1.4"/>')
add(f'<path d="{STAR}" fill="#ffffff"/>')
text(668, 382, "ImageReward", size=T_BODY, weight="bold", fill="#8f2a20", anchor="end")
rich(668, 408, [("R", 0, None, 1)], size=T_BODY, fill="#8f2a20")

rich(690, 512, [("q", 0, None, 1), ("b", 5, 15, 1), (" = min", -5, None, 1),
                ("i", 5, 15, 1), (" R(f", -5, None, 1), ("i", 5, 15, 1),
                (", p)", -5, None, 1)], size=T_FORM)
path_arrow("M 742 388 L 776 388 L 776 330 L 800 330", color=INK)


# ── router diamond ──────────────────────────────────────────────────────────
add('<polygon points="866,282 928,340 866,398 804,340" fill="#ffffff" stroke="#8a8a8a" stroke-width="2"/>')
rich(866, 348, [("q", 0, None, 1), ("b", 5, 15, 1), (" ≥ τ", -5, None, 1)], size=T_BODY)

# accept
path_arrow("M 928 340 L 1116 340", color=GRN, sw=4, marker="arrowgrn")
text(985, 312, "Accept", size=T_BODY, weight="bold", fill=GRN)
add(f'<path d="M 1012 318 l 11 15 22 -30" fill="none" stroke="{GRN}" stroke-width="4.5"/>')

# ── reject path: SDVG vs SDVG-hybrid ────────────────────────────────────────
# one rejected block's five states, twice. SDVG replays all four steps with the
# target; SDVG-hybrid takes the first k=3 from the drafter and lets the target
# finish the trajectory
rich(954, 210, [("T", 0, None, 1), ("  (14B)", 0, None, 1)], size=T_SUB, fill=ORG_S)

path_arrow("M 866 398 L 866 440", color=ORG_S, sw=4)
add(f'<path d="M 866 440 L 975 440" fill="none" stroke="{ORG_S}" stroke-width="4"/>')
for cx in (880, 975):
    path_arrow(f"M {cx} 440 L {cx} 468", color=ORG_S, sw=4, marker="arroworg")
text(884, 424, "Reject", size=T_BODY, weight="bold", fill=RED, anchor="start")
add(f'<path d="M 1042 398 l 26 26 M 1068 398 l -26 26" stroke="{RED}" stroke-width="4.5"/>')

TARGET_STATES = [("#fceee0", ORG_S), ("#f8dfc6", ORG_S), ("#f5d0ad", ORG_S),
                 ("#f2c194", ORG_S), ("#efb27a", ORG_S)]
DRAFT_STATES = [("#e9f3fc", BLUE_S), ("#cee2f4", BLUE_S), ("#b4d2ec", BLUE_S)]
CBW, CBH, CBG, CTY = 62, 22, 16, 470
for cx, states, name in [(880, TARGET_STATES, "SDVG"),
                         (975, DRAFT_STATES + TARGET_STATES[3:], "SDVG-hybrid")]:
    for i, (fill, stroke) in enumerate(states):
        y = CTY + i * (CBH + CBG)
        box(cx - CBW / 2, y, CBW, CBH, fill, stroke, rx=5, sw=1.7)
        if i < 4:
            nxt = states[i + 1][1]
            arrow(cx, y + CBH, cx, y + CBH + CBG, color=nxt, sw=2.0,
                  marker="arrowblue" if nxt == BLUE_S else "arroworg")
    text(cx, CTY + 5 * CBH + 4 * CBG + 22, name, size=T_SMALL, fill=GREY)

path_arrow("M 1008 548 L 1112 548", color=ORG_S, marker="arroworg")
text(1068, 512, "Regenerated", size=T_SMALL, fill=GREY)
rich(1068, 534, [("block ", 0, None, 0), ("x*", 0, None, 1), ("b", 5, 14, 1)], size=T_SMALL, fill=GREY)

# ── cascade scoring (hybrid) ────────────────────────────────────────────────
# the proxy scores four evenly spread frames, first and last included; only when
# it lands in the band around tau does the router score all twelve
PROXY = {0, 4, 7, 11}
for gy, green, note, spans in [
        (556, PROXY, "score 4 of 12", [("q̂", 0, None, 1), ("b", 5, 14, 1)]),
        (640, set(range(12)), "score all 12", [("q", 0, None, 1), ("b", 5, 14, 1)])]:
    for i in range(12):
        fill, stroke = ("#b7d9c0", GRN) if i in green else ("#e4e4e4", "#7a7a7a")
        add(f'<rect x="{548 + i * 12}" y="{gy}" width="10" height="22" rx="2" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
    text(548, gy - 8, note, size=T_SMALL - 3, fill=GREY, anchor="start")
    cy = gy + 11
    arrow(694, cy, 714, cy, color=INK, sw=2.2)
    add(f'<circle cx="728" cy="{cy}" r="13" fill="#c0392b" '
        f'stroke="#8f2a20" stroke-width="1.6"/>')
    add(f'<g transform="translate(728,{cy}) scale(0.5) translate(-710,-388)">'
        f'<path d="{STAR}" fill="#ffffff"/></g>')
    rich(762, cy + 5, spans, size=T_SMALL)

path_arrow("M 728 580 L 728 636", color=GRN, sw=2.2, dashed=True, marker="arrowgrn")
text(716, 606, "inconclusive", size=T_SMALL - 3, fill="#2f6b40", anchor="end")

# ── output ──────────────────────────────────────────────────────────────────
# the block sequence once block b has been decided, drawn for both outcomes.
# The six earlier blocks are the ones the Input panel already shows; the last
# one is block b, taken from the draft on accept and regenerated on reject
text(1280, 296, "KV Cache (Target)", size=T_BODY, weight="bold")
CACHE = [("#efb27a", ORG_S), ("#7fb0dd", BLUE_S), ("#7fb0dd", BLUE_S),
         ("#7fb0dd", BLUE_S), ("#efb27a", ORG_S), ("#7fb0dd", BLUE_S)]
for gy, tag, tagcol, last in [(324, "accept", GRN, ("#7fb0dd", BLUE_S)),
                              (532, "reject", RED, ("#efb27a", ORG_S))]:
    text(1180, gy + 22, tag, size=T_SMALL - 2, weight="bold", fill=tagcol,
         anchor="end")
    for i, (fill, stroke) in enumerate(CACHE + [last]):
        x = 1190 + i * 26
        add(f'<rect x="{x}" y="{gy}" width="24" height="32" rx="3" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        if i == 0:
            padlock(x + 4, gy + 13)

# ── legend ──────────────────────────────────────────────────────────────────
LEGEND = [
    ("#5f9fd6", "#3c78b4", "draft accepted", "fast, lower fidelity"),
    ("#e8853c", "#a85a20", "target regenerated", "high quality"),
]
LG_Y = 700
for i, (fill, stroke, label, note) in enumerate(LEGEND):
    x = 36 + i * 282
    box(x, LG_Y, 22, 22, fill, stroke, rx=5, sw=1.8)
    text(x + 32, LG_Y + 16, label, size=T_SMALL + 1, weight="bold", anchor="start")
    text(x + 32, LG_Y + 36, note, size=T_SMALL - 1, fill=GREY, anchor="start")

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
