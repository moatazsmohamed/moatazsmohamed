#!/usr/bin/env python3
"""
Self-hosted brand assets for the profile README — no third-party image services,
so nothing can 404, rate-limit or freeze:

  assets/hero-banner.svg   waving gradient banner with the name + role
  assets/typing-line.svg   looping typewriter line (pure CSS)
  assets/divider.svg       thin gradient section rule

Usage: python3 scripts/make_brand_assets.py
"""

import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

BG = "#0D1117"
CYAN = "#22D3EE"
VIOLET = "#8B5CF6"
MAGENTA = "#E879F9"
TEXT = "#E6EDF3"
DIM = "#8B949E"
SANS = "'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ banner ---
def hero_banner():
    W, H = 1200, 300
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-label="Moataz Mohamed — '
             f'Frontend Developer, Arabic-first web and mobile">')
    p.append("<defs>"
             f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{BG}"/>'
             f'<stop offset="0.55" stop-color="#120E24"/>'
             f'<stop offset="1" stop-color="#0B1220"/>'
             "</linearGradient>"
             f'<linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="#FFFFFF"/>'
             f'<stop offset="0.45" stop-color="{CYAN}"/>'
             f'<stop offset="1" stop-color="{VIOLET}"/>'
             "</linearGradient>"
             f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
             f'<stop offset="0" stop-color="{VIOLET}" stop-opacity="0.55"/>'
             f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>'
             "</radialGradient>"
             f'<linearGradient id="wave1" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.9"/>'
             f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>'
             "</linearGradient>"
             f'<linearGradient id="wave2" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{MAGENTA}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{MAGENTA}" stop-opacity="0.75"/>'
             f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>'
             "</linearGradient>"
             "<style>"
             "text{font-family:" + SANS + "}"
             ".name{font-size:96px;font-weight:800;letter-spacing:12px}"
             ".role{font-size:21px;letter-spacing:5.5px;font-weight:600}"
             ".loc{font-size:14px;letter-spacing:2.6px}"
             "@keyframes drift{0%{transform:translateX(-60px)}"
             "50%{transform:translateX(60px)}100%{transform:translateX(-60px)}}"
             "@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}"
             ".w1{animation:drift 14s ease-in-out infinite}"
             ".w2{animation:drift 18s ease-in-out infinite reverse}"
             ".dot{animation:pulse 4s ease-in-out infinite}"
             "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
             "</style></defs>")

    p.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    p.append(f'<ellipse cx="{W*0.5}" cy="96" rx="430" ry="150" fill="url(#glow)"/>')

    p.append('<g fill="#FFFFFF" opacity="0.06">')
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

    p.append(f'<text class="name" x="{W/2}" y="140" text-anchor="middle" '
             f'fill="url(#ink)">MOATAZ</text>')
    p.append(f'<line x1="{W/2-150}" y1="164" x2="{W/2+150}" y2="164" '
             f'stroke="{CYAN}" stroke-opacity="0.55" stroke-width="1.5"/>')
    p.append(f'<text class="role" x="{W/2}" y="198" text-anchor="middle" '
             f'fill="{CYAN}">FRONTEND DEVELOPER</text>')
    p.append(f'<text class="loc" x="{W/2}" y="226" text-anchor="middle" '
             f'fill="{DIM}">ARABIC-FIRST WEB &amp; MOBILE · ALEXANDRIA, EGYPT</text>')
    p.append("</svg>")
    return "".join(p)


# ------------------------------------------------------------------ typing ---
def typing_line():
    phrases = [
        "Frontend Developer · Arabic-first by design",
        "React · Next.js · TypeScript · Supabase",
        "IT Student @ Borg El Arab Technological University",
        "وابنِ واجهات تُقرأ صح في الاتجاهين",
    ]
    W, H = 900, 46
    size = 21
    char_w = size * 0.6
    cycle = 4.0 * len(phrases)

    widths = [int(len(p) * char_w) + 16 for p in phrases]

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" role="img" aria-label="'
             f'{esc(phrases[0])}">')
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
        p.append(f".c{i}{{animation:type{i} {cycle}s steps(28,end) "
                 f"{i*4.0}s infinite}}")

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
                 f'<text x="{W/2}" y="31" text-anchor="middle" fill="{CYAN}">'
                 f'{esc(phrase)}</text></g></g>')

    p.append(f'<rect class="cur" x="{W/2-6}" y="14" width="10" height="20" fill="{CYAN}"/>')
    p.append("</svg>")
    return "".join(p)


# ----------------------------------------------------------------- divider ---
def divider():
    W, H = 1200, 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="section divider">'
            f'<defs><linearGradient id="d" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
            f'<stop offset="0.2" stop-color="{CYAN}" stop-opacity="0.85"/>'
            f'<stop offset="0.55" stop-color="{VIOLET}" stop-opacity="0.85"/>'
            f'<stop offset="0.85" stop-color="{MAGENTA}" stop-opacity="0.6"/>'
            f'<stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/>'
            f'</linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#d)"/></svg>')


def main():
    os.makedirs(ASSETS, exist_ok=True)
    files = {
        "hero-banner.svg": hero_banner(),
        "typing-line.svg": typing_line(),
        "divider.svg": divider(),
    }
    for name, svg in files.items():
        path = os.path.join(ASSETS, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"{path} · {len(svg)/1024:.1f} KB")


if __name__ == "__main__":
    main()
