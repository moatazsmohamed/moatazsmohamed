#!/usr/bin/env python3
"""Project cards — one self-contained SVG per project.

Each card embeds its screenshot as a base64 JPEG, so the file survives GitHub's
image proxy with no external request: an SVG loaded through <img> is not allowed
to fetch anything. Motion is SMIL (see docs/HOW-IT-WORKS.md): a slow Ken Burns
drift on the shot, a light sweep that crosses the frame every few seconds, and
a caption that lifts into place once.

Base state of every element is its finished state — a renderer that ignores
motion still shows the full screenshot with its caption in place.
"""
import base64
import io
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "projects")
SHOTS = "/home/ubuntu/profile/shots"

W, H = 1000, 563
ACCENT = "#FF4438"
INK = "#FFFFFF"
DIM = "rgba(255,255,255,0.66)"
SANS = ("'Inter','Helvetica Neue',Helvetica,Arial,sans-serif")
MONO = ("'JetBrains Mono','SFMono-Regular',Menlo,Consolas,monospace")


def embed(path, quality=62):
    """Cover-crop to the card ratio, re-encode small, return a data URI."""
    im = Image.open(path).convert("RGB")
    tw, th = W, H
    scale = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = (im.height - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p, index, total, dur):
    data = embed(p["shot"])
    uid = p["slug"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p['name'])} — {esc(p['kind'])}, live preview">
<defs>
<clipPath id="c{uid}"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<linearGradient id="s{uid}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000" stop-opacity="0"/>
<stop offset="0.55" stop-color="#000" stop-opacity="0.55"/>
<stop offset="1" stop-color="#000" stop-opacity="0.92"/>
</linearGradient>
<linearGradient id="t{uid}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000" stop-opacity="0.55"/>
<stop offset="1" stop-color="#000" stop-opacity="0"/>
</linearGradient>
<linearGradient id="w{uid}" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/>
<stop offset="0.5" stop-color="#fff" stop-opacity="0.16"/>
<stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
</defs>
<g clip-path="url(#c{uid})">
<image href="{data}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" style="transform-origin:{W/2}px {H/2}px">
<animateTransform attributeName="transform" type="scale" values="1;1.055;1" dur="{dur}s" repeatCount="indefinite"/>
</image>
<rect width="{W}" height="150" fill="url(#t{uid})"/>
<rect width="{W}" height="{H}" fill="url(#s{uid})"/>
<g transform="skewX(-16)" opacity="0.9">
<rect x="-320" y="-120" width="260" height="{H+240}" fill="url(#w{uid})">
<animateTransform attributeName="transform" type="translate" values="-300 0;-300 0;1500 0;1500 0" keyTimes="0;0.80;0.93;1" dur="9s" repeatCount="indefinite"/>
</rect>
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="rgba(255,255,255,0.16)"/>
</g>
<text x="30" y="40" font-family="{MONO}" font-size="12.5" letter-spacing="2.6" fill="rgba(255,255,255,0.62)">{index:02d} — {total:02d}</text>
<text x="{W-30}" y="40" text-anchor="end" font-family="{MONO}" font-size="12.5" letter-spacing="2.6" fill="{ACCENT}">LIVE <tspan fill="{ACCENT}"><animate attributeName="opacity" values="1;1;0.25;0.25" keyTimes="0;0.5;0.55;1" dur="1.8s" repeatCount="indefinite"/>&#8599;</tspan></text>
<g>
<animateTransform attributeName="transform" type="translate" values="0 12;0 12;0 0;0 0" keyTimes="0;0.04;0.13;1" dur="6s" fill="freeze"/>
<rect x="30" y="{H-96}" width="52" height="3" fill="{ACCENT}"/>
<text x="30" y="{H-58}" font-family="{SANS}" font-size="35" font-weight="800" letter-spacing="0.6" fill="{INK}">{esc(p['name'])}</text>
<text x="30" y="{H-30}" font-family="{MONO}" font-size="14.5" letter-spacing="1.4" fill="{DIM}">{esc(p['kind'])}</text>
<text x="{W-30}" y="{H-30}" text-anchor="end" font-family="{MONO}" font-size="14" letter-spacing="1" fill="rgba(255,255,255,0.82)">{esc(p['stack'])}</text>
</g>
</svg>
'''


PROJECTS = [
    dict(slug="m3t", name="M3T PORTFOLIO", kind="MY OWN SPACE · AR / EN",
         stack="Next.js · better-auth · GSAP", shot=os.path.join(ASSETS, "m3t-hero.jpg"), dur=26),
    dict(slug="sanad", name="SANAD", kind="AI ACADEMIC ECOSYSTEM",
         stack="React · tRPC · Drizzle · Neon", shot=os.path.join(SHOTS, "sanad.png"), dur=23),
    dict(slug="social", name="SOCIAL INTELLIGENCE", kind="ANALYTICS DASHBOARD",
         stack="React 19 · Supabase · Recharts", shot=os.path.join(SHOTS, "social.png"), dur=29),
    dict(slug="zakhraf", name="ZAKHRAF", kind="ARABIC DESIGN HOUSE",
         stack="HTML · CSS · Vanilla JS", shot=os.path.join(SHOTS, "zakhraf.png"), dur=25),
    dict(slug="wood", name="MS WOODWORKS", kind="CLIENT SITE · WOOD ATELIER",
         stack="Express · PostgreSQL", shot=os.path.join(SHOTS, "wood.png"), dur=27),
    dict(slug="tasheela", name="TASHEELA", kind="ACCOUNTING & OPS PLATFORM",
         stack="React · tRPC · Drizzle", shot=os.path.join(SHOTS, "tasheela.png"), dur=24),
]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    total = len(PROJECTS)
    for i, p in enumerate(PROJECTS, start=1):
        svg = card(p, i, total, p["dur"])
        out = os.path.join(ASSETS, f"card-{p['slug']}.svg")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"assets/projects/card-{p['slug']}.svg · {len(svg)/1024:.0f} KB")


if __name__ == "__main__":
    main()