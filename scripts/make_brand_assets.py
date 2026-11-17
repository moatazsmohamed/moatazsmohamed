#!/usr/bin/env python3
"""
Self-hosted brand assets for the profile README — no third-party image services,
so nothing can 404, rate-limit or freeze. Every asset ships in a dark and a
light variant so the README respects the visitor's colour scheme.

  assets/hero-banner.svg          + -light
  assets/typing-line.svg          + -light
  assets/divider.svg              (theme neutral, gradient only)

Usage: python3 scripts/make_brand_assets.py
"""

import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

SANS = "'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark": {
        "bg1": "#0A0A0A", "bg2": "#131313", "bg3": "#0A0A0A",
        "ink1": "#FAFAF9", "ink2": "#FF4438", "ink3": "#FAFAF9",
        "cyan": "#FF4438", "violet": "#FF4438", "magenta": "#FF8A80",
        "dim": "#8A8A85", "dots": "#FAFAF9", "dot_op": "0.05", "glow_op": "0.5",
    },
    "light": {
        "bg1": "#FFFFFF", "bg2": "#FAF9F6", "bg3": "#FFFFFF",
        "ink1": "#0A0A0A", "ink2": "#D92B1E", "ink3": "#0A0A0A",
        "cyan": "#D92B1E", "violet": "#B91C1C", "magenta": "#8C1F14",
        "dim": "#6B6B66", "dots": "#0A0A0A", "dot_op": "0.05", "glow_op": "0.10",
    },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ banner ---
def hero_banner(t):
    W, H = 1200, 300
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-label="Moataz Mohamed — '
             f'Frontend Developer, Arabic-first web and mobile">')
    p.append("<defs>"
             f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{t["bg1"]}"/>'
             f'<stop offset="0.55" stop-color="{t["bg2"]}"/>'
             f'<stop offset="1" stop-color="{t["bg3"]}"/>'
             "</linearGradient>"
             f'<linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["ink1"]}"/>'
             f'<stop offset="0.45" stop-color="{t["ink2"]}"/>'
             f'<stop offset="1" stop-color="{t["ink3"]}"/>'
             "</linearGradient>"
             f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
             f'<stop offset="0" stop-color="{t["violet"]}" stop-opacity="0.55"/>'
             f'<stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/>'
             "</radialGradient>"
             f'<linearGradient id="wave1" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["cyan"]}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{t["cyan"]}" stop-opacity="0.9"/>'
             f'<stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/>'
             "</linearGradient>"
             f'<linearGradient id="wave2" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["magenta"]}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{t["magenta"]}" stop-opacity="0.75"/>'
             f'<stop offset="1" stop-color="{t["cyan"]}" stop-opacity="0"/>'
             "</linearGradient>"
             "<style>"
             "text{font-family:" + SANS + "}"
             ".name{font-size:96px;font-weight:800;letter-spacing:12px}"
             ".role{font-size:21px;letter-spacing:5.5px;font-weight:600}"
             ".loc{font-size:14px;letter-spacing:2.6px}"
             ".meta{font-family:" + MONO + ";font-size:10.5px;letter-spacing:2.4px}"
             "@keyframes drift{0%{transform:translateX(-60px)}"
             "50%{transform:translateX(60px)}100%{transform:translateX(-60px)}}"
             "@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}"
             ".w1{animation:drift 14s ease-in-out infinite}"
             ".w2{animation:drift 18s ease-in-out infinite reverse}"
             ".dot{animation:pulse 4s ease-in-out infinite}"
             "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
             "</style></defs>")

    p.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    p.append(f'<ellipse cx="{W*0.5}" cy="96" rx="430" ry="150" fill="url(#glow)" '
             f'opacity="{t["glow_op"]}"/>')

    p.append(f'<g fill="{t["dots"]}" opacity="{t["dot_op"]}">')
    for y in range(24, 220, 26):
        for x in range(24, W - 20, 26):
            p.append(f'<circle class="dot" cx="{x}" cy="{y}" r="1.1"/>')
    p.append("</g>")

    p.append(f'<g class="w1"><path d="M-80 278 C 160 232, 380 306, 640 266 '
             f'S 1080 232, 1290 274" fill="none" stroke="url(#wave1)" stroke-width="2.5"/>'
             f'<path d="M-80 296 C 180 256, 400 322, 660 286 S 1100 254, 1290 294" '
             f'fill="none" stroke="url(#wave1)" stroke-width="1.6" stroke-opacity="0.6"/></g>')
    p.append(f'<g class="w2"><path d="M-80 250 C 200 210, 420 284, 680 244 '
             f'S 1060 210, 1290 254" fill="none" stroke="url(#wave2)" stroke-width="1.4" '
             f'stroke-opacity="0.7"/></g>')

    # editorial furniture: hairline rules + monospaced micro labels
    p.append(f'<line x1="0" y1="24.5" x2="{W}" y2="24.5" stroke="{t["ink1"]}" '
             f'stroke-opacity="0.10"/>')
    p.append(f'<text class="meta" x="34" y="17" fill="{t["dim"]}">'
             f'M3T — PROFILE</text>')
    p.append(f'<text class="meta" x="{W-34}" y="17" text-anchor="end" '
             f'fill="{t["cyan"]}">OPEN TO WORK</text>')

    p.append(f'<text class="name" x="{W/2}" y="140" text-anchor="middle" '
             f'fill="url(#ink)">MOATAZ</text>')
    p.append(f'<line x1="{W/2-150}" y1="164" x2="{W/2+150}" y2="164" '
             f'stroke="{t["cyan"]}" stroke-opacity="0.55" stroke-width="1.5"/>')
    p.append(f'<text class="role" x="{W/2}" y="198" text-anchor="middle" '
             f'fill="{t["cyan"]}">FRONTEND DEVELOPER</text>')
    p.append(f'<text class="loc" x="{W/2}" y="226" text-anchor="middle" '
             f'fill="{t["dim"]}">ARABIC-FIRST WEB &amp; MOBILE · ALEXANDRIA, EGYPT</text>')
    p.append("</svg>")
    return "".join(p)


# ------------------------------------------------------------------ typing ---
def typing_line(t):
    phrases = [
        "Frontend Developer · Arabic-first by design",
        "React · Next.js · TypeScript · Supabase",
        "IT Student @ Borg El Arab Technological University",
        "وابنِ واجهات تُقرأ صح في الاتجاهين",
    ]
    W, H = 760, 42
    size = 19
    char_w = size * 0.6
    cycle = 4.0 * len(phrases)
    widths = [int(len(p) * char_w) + 16 for p in phrases]

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(phrases[0])}">')
    p.append("<defs><style>")
    p.append(f"text{{font-family:{MONO};font-size:{size}px}}")
    p.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    p.append(".cur{animation:blink 1s steps(1,end) infinite}")

    for i, w in enumerate(widths):
        p.append(f"@keyframes show{i}{{0%{{opacity:0}}1%{{opacity:1}}"
                 f"88%{{opacity:1}}92%{{opacity:0}}100%{{opacity:0}}}}")
        p.append(f"@keyframes type{i}{{0%{{transform:translateX(-{w}px)}}"
                 f"1%{{transform:translateX(-{w}px)}}"
                 f"17%{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}")
        p.append(f".ph{i}{{opacity:0;animation:show{i} {cycle}s linear "
                 f"{i*4.0}s infinite}}")
        p.append(f".c{i}{{animation:type{i} {cycle}s steps(28,end) {i*4.0}s infinite}}")

    p.append("@media (prefers-reduced-motion:reduce){")
    p.append(".ph0{opacity:1;animation:none}.cur{display:none}")
    for i in range(len(widths)):
        p.append(f".c{i}{{animation:none}}")
    p.append("}</style>")

    for i, w in enumerate(widths):
        p.append(f'<mask id="c{i}" maskUnits="userSpaceOnUse" x="0" y="0" '
                 f'width="{W}" height="{H}">'
                 f'<rect class="c{i}" x="{W/2 - w/2:.0f}" y="0" width="{w}" '
                 f'height="{H}" fill="#fff"/></mask>')
    p.append("</defs>")

    for i, phrase in enumerate(phrases):
        p.append(f'<g class="ph{i}"><g mask="url(#c{i})">'
                 f'<text x="{W/2}" y="28" text-anchor="middle" fill="{t["cyan"]}">'
                 f'{esc(phrase)}</text></g></g>')

    p.append(f'<rect class="cur" x="{W/2 + max(widths)/2 + 4:.0f}" y="13" '
             f'width="9" height="18" fill="{t["cyan"]}"/>')
    p.append("</svg>")
    return "".join(p)


# ----------------------------------------------------------------- divider ---
def divider():
    """Theme neutral: a gradient rule with no background, readable on both."""
    W, H = 1200, 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="section divider">'
            f'<defs><linearGradient id="d" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#FF4438" stop-opacity="0"/>'
            f'<stop offset="0.18" stop-color="#FF4438" stop-opacity="0.75"/>'
            f'<stop offset="0.5" stop-color="#FF4438" stop-opacity="0.9"/>'
            f'<stop offset="0.82" stop-color="#FF4438" stop-opacity="0.75"/>'
            f'<stop offset="1" stop-color="#FF4438" stop-opacity="0"/>'
            f'</linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#d)"/></svg>')


# ------------------------------------------------------------------ footer ---
def footer(t):
    W, H = 1200, 150
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-label="Thanks for stopping by — '
             f'Moataz Mohamed, Alexandria, Egypt">')
    p.append("<defs>"
             f'<linearGradient id="fbg" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{t["bg1"]}"/>'
             f'<stop offset="0.6" stop-color="{t["bg2"]}"/>'
             f'<stop offset="1" stop-color="{t["bg3"]}"/>'
             "</linearGradient>"
             f'<linearGradient id="fw" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{t["cyan"]}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{t["cyan"]}" stop-opacity="0.8"/>'
             f'<stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/>'
             "</linearGradient>"
             "<style>"
             "text{font-family:" + SANS + "}"
             ".fname{font-size:26px;font-weight:800;letter-spacing:7px}"
             ".ftag{font-size:13px;letter-spacing:3px}"
             ".fmeta{font-size:11.5px;letter-spacing:2.2px}"
             "@keyframes drift{0%{transform:translateX(-40px)}"
             "50%{transform:translateX(40px)}100%{transform:translateX(-40px)}}"
             ".w{animation:drift 16s ease-in-out infinite}"
             "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
             "</style></defs>")

    p.append(f'<rect width="{W}" height="{H}" fill="url(#fbg)"/>')
    p.append(f'<g class="w"><path d="M-60 130 C 200 108, 420 152, 660 124 '
             f'S 1060 104, 1280 134" fill="none" stroke="url(#fw)" stroke-width="2"/>'
             f'<path d="M-60 144 C 220 126, 440 166, 680 140 S 1080 122, 1280 148" '
             f'fill="none" stroke="url(#fw)" stroke-width="1.2" stroke-opacity="0.55"/></g>')
    p.append(f'<text class="fname" x="{W/2}" y="62" text-anchor="middle" '
             f'fill="{t["ink1"]}">MOATAZ MOHAMED</text>')
    p.append(f'<text class="ftag" x="{W/2}" y="86" text-anchor="middle" '
             f'fill="{t["cyan"]}">FRONTEND DEVELOPER · ARABIC-FIRST</text>')
    p.append(f'<text class="fmeta" x="{W/2}" y="108" text-anchor="middle" '
             f'fill="{t["dim"]}" opacity="0.75">ALEXANDRIA, EGYPT · THANKS FOR '
             f'STOPPING BY</text>')
    p.append("</svg>")
    return "".join(p)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    written = []
    for name, t in THEMES.items():
        suffix = "" if name == "dark" else "-light"
        files = {
            f"hero-banner{suffix}.svg": hero_banner(t),
            f"typing-line{suffix}.svg": typing_line(t),
            f"footer{suffix}.svg": footer(t),
        }
        for fname, svg in files.items():
            path = os.path.join(ASSETS, fname)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(svg)
            written.append((fname, len(svg)))

    with open(os.path.join(ASSETS, "divider.svg"), "w", encoding="utf-8") as fh:
        fh.write(divider())
    written.append(("divider.svg", os.path.getsize(os.path.join(ASSETS, "divider.svg"))))

    for fname, size in written:
        print(f"assets/{fname} · {size/1024:.1f} KB")


if __name__ == "__main__":
    main()
