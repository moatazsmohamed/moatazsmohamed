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
BG = "#0D1117"
BAR = "#161B22"
STROKE = "#21262D"
CYAN = "#22D3EE"
MAGENTA = "#E879F9"
GREEN = "#3FB950"
DIM = "#8B949E"
TEXT = "#C9D1D9"

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
    for band in range(BANDS):
        if band not in by_band:
            continue
        delay = 0 if static else start + band * per_band_delay
        style = f' style="animation-delay:{delay:.2f}s"' if not static else ""
        out.append(f'<g class="band"{style}>')
        for colour, cells in by_band[band]:
            out.append(f'<g fill="{colour}">')
            for gx, gy in cells:
                x = PORT_X + gx * PITCH
                y = PORT_Y + gy * PITCH
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{DOT}" height="{DOT}"/>')
            out.append("</g>")
        out.append("</g>")
    return "".join(out), start + BANDS * per_band_delay + 0.3


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(avatar_path, out_path, static=False):
    dots = load_dots(avatar_path)
    portrait, paint_done = portrait_svg(dots, static)

    cmd = "neofetch --dots --profile"
    cmd_w = int(9.6 * len(cmd)) + 8

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
        ".band{opacity:1;animation:paint .24s ease-out backwards}"
        ".row{opacity:1;animation:fade .32s ease-out backwards}"
        ".typerect{animation:widen 1.05s steps(26,end) .35s backwards}"
        ".cursor{animation:blink 1.1s steps(1,end) infinite}"
        "@keyframes paint{from{opacity:0}to{opacity:1}}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        "@keyframes widen{from{width:0}to{width:%dpx}}"
        "@keyframes blink{0%%,49%%{opacity:1}50%%,100%%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    ) % cmd_w

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Animated terminal that '
        f"paints Moataz Mohamed's portrait from {len(dots)} real-colour dots, "
        f'followed by a neofetch-style profile readout">'
    )
    parts.append("<defs><style>" + css + "</style>"
                 f'<clipPath id="typeclip"><rect class="typerect" x="0" y="40" '
                 f'width="{cmd_w}" height="30"/></clipPath></defs>')

    parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" '
                 f'fill="{BG}" stroke="{STROKE}"/>')
    parts.append(f'<path d="M0.5 14.5a14 14 0 0 1 14-14h{W-29}a14 14 0 0 1 14 14v20H0.5z" '
                 f'fill="{BAR}"/>')
    parts.append(f'<line x1="0.5" y1="34.5" x2="{W-0.5}" y2="34.5" stroke="{STROKE}"/>')
    for i, colour in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        parts.append(f'<circle cx="{22 + i*18}" cy="17.5" r="5.5" fill="{colour}"/>')
    parts.append(f'<text x="{W/2}" y="21.5" text-anchor="middle" fill="{DIM}" '
                 f'font-size="11.5">moataz@github — zsh — 120×32</text>')

    parts.append(f'<text class="mono" x="26" y="63" fill="{GREEN}">moataz@github</text>'
                 f'<text class="mono" x="134" y="63" fill="{CYAN}">~</text>'
                 f'<text class="mono" x="150" y="63" fill="{DIM}">%</text>')
    clip = "" if static else ' clip-path="url(#typeclip)"'
    parts.append(f'<g{clip}><text class="mono" x="168" y="63" '
                 f'fill="{TEXT}">{esc(cmd)}</text></g>')
    parts.append(f'<rect class="cursor" x="{168 + cmd_w + 3}" y="51" width="8" '
                 f'height="15" fill="{CYAN}"/>')

    parts.append(portrait)

    name_y = info_top
    parts.append(f'<text class="mono" x="{info_x}" y="{name_y}" fill="{CYAN}" '
                 f'font-size="14" font-weight="700">moataz@github</text>')
    parts.append(f'<line x1="{info_x}" y1="{name_y + 8}" x2="{info_x + 112}" '
                 f'y2="{name_y + 8}" stroke="{CYAN}" stroke-opacity="0.45"/>')

    for i, (k, v) in enumerate(rows):
        y = name_y + 34 + i * row_h
        delay = 0 if static else paint_done * 0.35 + 0.85 + i * 0.15
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        parts.append(
            f'<g class="row"{style}>'
            f'<text class="k" x="{info_x}" y="{y:.0f}">{esc(k)}</text>'
            f'<text class="k" x="{info_x + 72}" y="{y:.0f}" fill="{MAGENTA}">.</text>'
            f'<text class="v" x="{info_x + 130}" y="{y:.0f}">{esc(v)}</text></g>'
        )

    sw_y = name_y + 34 + len(rows) * row_h + 6
    for i, colour in enumerate([BG, "#30363D", "#484F58", CYAN, "#8B5CF6", MAGENTA, GREEN, TEXT]):
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
