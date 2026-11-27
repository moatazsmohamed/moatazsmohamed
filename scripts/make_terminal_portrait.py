#!/usr/bin/env python3
"""
Generates assets/terminal-portrait.svg — an animated "neofetch" terminal whose
portrait is painted dot by dot from the GitHub avatar.

No JavaScript, no external services, no SMIL: the animation is pure CSS inside
the SVG, so it also plays when GitHub serves the file through <img>. If a
renderer ignores CSS animation the SVG still shows the finished portrait,
because the base state of every element is "visible".

Usage:  python3 scripts/make_terminal_portrait.py [avatar.png] [out.svg] [--static]
"""

import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 940, 452
BG = "#0A0A0A"
BAR = "#141414"
STROKE = "#262626"
CYAN = "#ffff23"          # the single signal accent
MAGENTA = "#ffff8a"
GREEN = "#FAFAF9"         # hostname reads as plain ink, not a second accent
DIM = "#7C7C76"
TEXT = "#D8D8D3"
DUO_LO = (18, 18, 18)     # portrait ramp: ink
DUO_HI = (250, 250, 249)  # portrait ramp: paper
MONO_PORTRAIT = True      # False keeps the avatar's original colours

GRID = 48           # dots per side
PITCH = 4.9         # px between dot origins
DOT = 4.2           # dot size
PORT_X = 26.0
PORT_Y = 92.0
PALETTE_SIZE = 14
BANDS = 12


def load_dots(path):
    im = Image.open(path).convert("RGB")
    im = im.resize((GRID, GRID), Image.LANCZOS)
    im = im.quantize(colors=PALETTE_SIZE, method=Image.MEDIANCUT).convert("RGB")
    px = im.load()
    dots = []
    for gy in range(GRID):
        for gx in range(GRID):
            r, g, b = px[gx, gy]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 14:            # near-black background -> leave the cell empty
                continue
            if MONO_PORTRAIT:
                # duotone: press the avatar into a single ink -> paper ramp so the
                # red stays reserved for the interface chrome
                k = (lum / 255.0) ** 0.85
                r, g, b = (round(lo + (hi - lo) * k)
                           for lo, hi in zip(DUO_LO, DUO_HI))
            dots.append((gx, gy, "#%02X%02X%02X" % (r, g, b)))
    return dots


def band_of(gy):
    return min(BANDS - 1, gy * BANDS // GRID)


def portrait_svg(dots, static):
    buckets = {}
    for gx, gy, colour in dots:
        buckets.setdefault((band_of(gy), colour), []).append((gx, gy))

    by_band = {}
    for band, colour in sorted(buckets):
        by_band.setdefault(band, []).append((colour, buckets[(band, colour)]))

    out = []
    per_band_delay = 0.13
    start = 1.5
    PAINT_T = start + BANDS * per_band_delay + 0.3
    for band in range(BANDS):
        if band not in by_band:
            continue
        delay = 0 if static else start + band * per_band_delay
        anim = ""
        if not static:
            anim = smil_fade(delay, 0.24, PAINT_T)
        out.append(f'<g opacity="1">{anim}')
        for colour, cells in by_band[band]:
            out.append(f'<g fill="{colour}">')
            for gx, gy in cells:
                x = PORT_X + gx * PITCH
                y = PORT_Y + gy * PITCH
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{DOT}" height="{DOT}"/>')
            out.append("</g>")
        out.append("</g>")
    return "".join(out), PAINT_T


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def smil_fade(delay, length, total, frm="0", to="1"):
    """A one-shot fade expressed as absolute fractions of one shared timeline.

    begin stays at 0 for every element, so there is no pre-begin state to
    flash: the element is simply held at `frm` until its slot opens.
    """
    k0 = max(0.0, min(0.999, delay / total))
    k1 = max(k0 + 0.001, min(0.9995, (delay + length) / total))
    return (f'<animate attributeName="opacity" values="{frm};{frm};{to};{to}" '
            f'keyTimes="0;{k0:.4f};{k1:.4f};1" dur="{total:.2f}s" '
            f'begin="0s" fill="freeze"/>')


def build(avatar_path, out_path, static=False):
    dots = load_dots(avatar_path)
    portrait, paint_done = portrait_svg(dots, static)

    cmd = "neofetch --dots --profile"
    cmd_w = int(9.6 * len(cmd)) + 8
    type_anim = (f'<animateTransform attributeName="transform" type="translate" '
                 f'values="-{cmd_w} 0;-{cmd_w} 0;0 0;0 0" keyTimes="0;0.12;0.42;1" '
                 f'dur="{cmd_w / 260:.2f}s" begin="0.2s" fill="freeze"/>')

    rows = [
        ("OS", "Alexandria, Egypt"),
        ("Role", "Frontend Developer"),
        ("Focus", "Arabic-first web & mobile"),
        ("Shell", "zsh 5.9"),
        ("Editor", "VS Code · Cursor"),
        ("Stack", "React · Next.js · TypeScript"),
        ("Data", "Supabase · PostgreSQL"),
        ("Motion", "GSAP · Framer Motion"),
        ("Study", "IT @ BATU"),
        ("Live", "6 deployments in production"),
    ]

    info_x = 306
    row_h = 21.5
    info_top = 96.0

    css = (
        "text{font-family:'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,"
        "Menlo,Consolas,monospace}"
        f".k{{fill:{DIM};font-size:12.5px}}"
        f".v{{fill:{TEXT};font-size:12.5px}}"
        ".mono{font-size:12.5px}"
    )

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Animated terminal that '
        f"paints Moataz Mohamed's portrait from {len(dots)} real-colour dots, "
        f'followed by a neofetch-style profile readout">'
    )
    parts.append("<defs><style>" + css + "</style>"
                 f'<mask id="typeclip" maskUnits="userSpaceOnUse" x="0" y="40" '
                 f'width="{W}" height="40"><rect x="168" y="40" width="{cmd_w}" '
                 f'height="34" fill="#fff">{"" if static else type_anim}</rect>'
                 f'</mask></defs>')

    parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" '
                 f'fill="{BG}" stroke="{STROKE}"/>')
    parts.append(f'<path d="M0.5 14.5a14 14 0 0 1 14-14h{W-29}a14 14 0 0 1 14 14v20H0.5z" '
                 f'fill="{BAR}"/>')
    parts.append(f'<line x1="0.5" y1="34.5" x2="{W-0.5}" y2="34.5" stroke="{STROKE}"/>')
    for i, colour in enumerate(("#3A3A3A", "#4A4A4A", "#5A5A5A")):
        parts.append(f'<circle cx="{22 + i*18}" cy="17.5" r="5.5" fill="{colour}"/>')
    parts.append(f'<text x="{W/2}" y="21.5" text-anchor="middle" fill="{DIM}" '
                 f'font-size="11.5">moataz@github — zsh — 120×32</text>')

    parts.append(f'<text class="mono" x="26" y="63" fill="{GREEN}">moataz@github</text>'
                 f'<text class="mono" x="134" y="63" fill="{CYAN}">~</text>'
                 f'<text class="mono" x="150" y="63" fill="{DIM}">%</text>')
    clip = "" if static else ' mask="url(#typeclip)"' 
    parts.append(f'<g{clip}><text class="mono" x="168" y="63" '
                 f'fill="{TEXT}">{esc(cmd)}</text></g>')
    parts.append(f'<rect x="{168 + cmd_w + 3}" y="51" width="8" height="15" fill="{CYAN}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" '
                 f'keyTimes="0;0.49;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
                 f'</rect>')

    parts.append(portrait)

    name_y = info_top
    parts.append(f'<text class="mono" x="{info_x}" y="{name_y}" fill="{CYAN}" '
                 f'font-size="14" font-weight="700">moataz@github</text>')
    parts.append(f'<line x1="{info_x}" y1="{name_y + 8}" x2="{info_x + 112}" '
                 f'y2="{name_y + 8}" stroke="{CYAN}" stroke-opacity="0.45"/>')

    for i, (k, v) in enumerate(rows):
        y = name_y + 34 + i * row_h
        row_start = paint_done * 0.35 + 0.85
        row_t = row_start + len(rows) * 0.15 + 0.4
        anim = "" if static else smil_fade(row_start + i * 0.15, 0.32, row_t)
        parts.append(
            f'<g opacity="1">{anim}'
            f'<text class="k" x="{info_x}" y="{y:.0f}">{esc(k)}</text>'
            f'<text class="k" x="{info_x + 72}" y="{y:.0f}" fill="{MAGENTA}">.</text>'
            f'<text class="v" x="{info_x + 130}" y="{y:.0f}">{esc(v)}</text></g>'
        )

    sw_y = name_y + 34 + len(rows) * row_h + 6
    # a tonal ramp instead of a rainbow: ink -> paper, closed by the one accent
    for i, colour in enumerate([BG, "#262626", "#3F3F3F", "#5C5C5C",
                                "#8A8A85", "#B5B5B0", TEXT, CYAN]):
        parts.append(f'<rect x="{info_x + i*22}" y="{sw_y:.0f}" width="18" height="9" '
                     f'rx="2" fill="{colour}"/>')

    parts.append(f'<text class="mono" x="26" y="{H-18}" fill="{GREEN}">moataz@github</text>'
                 f'<text class="mono" x="134" y="{H-18}" fill="{CYAN}">~</text>'
                 f'<text class="mono" x="150" y="{H-18}" fill="{DIM}">%</text>'
                 f'<rect class="cursor" x="168" y="{H-30}" width="8" height="15" fill="{CYAN}"/>')

    parts.append("</svg>")

    svg = "".join(parts)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"{out_path}: {len(svg)/1024:.1f} KB · {len(dots)} dots · "
          f"paint done at {paint_done:.2f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    static = "--static" in sys.argv
    avatar = args[0] if len(args) > 0 else os.path.join(HERE, "assets", "avatar.png")
    out = args[1] if len(args) > 1 else os.path.join(HERE, "assets", "terminal-portrait.svg")
    build(avatar, out, static)
