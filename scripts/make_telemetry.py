#!/usr/bin/env python3
# Copyright (c) 2026 Moataz Mohamed (@moatazsmohamed). All rights reserved.
# Unauthorized copying, redistribution or reuse is prohibited. See LICENSE.
# Authorship marker: mm-aa947cabaa72f985
"""
Builds the self-hosted "Live Telemetry" panels for the profile README, in a dark
and a light variant each:

  assets/telemetry.svg            total contributions · current streak · longest streak
  assets/activity-graph.svg       daily contributions, last 30 days
  assets/language-spectrum.svg    language mix across public repositories
  assets/contribution-matrix.svg  53 x 7 pixel matrix of the contribution year

Everything is drawn locally from the GitHub API, so the README never depends on
a third-party stats service that can rate-limit or go down.

Auth: GITHUB_TOKEN (or GH_TOKEN) in the environment.
Usage: python3 scripts/make_telemetry.py
"""

import datetime as dt
import json
import math
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")
USER = "moatazsmohamed"

MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Segoe UI',Ubuntu,-apple-system,Helvetica,Arial,sans-serif"

THEMES = {
    "dark": {
        "panel": "#0A0A0A", "stroke": "#242424", "grid": "#1A1A1A",
        "text": "#D8D8D3", "title": "#FAFAF9", "dim": "#8A8A85",
        "cyan": "#ffff23", "violet": "#ffff8a", "magenta": "#ada614", "green": "#ffff23",
        "levels": ["#141414", "#33300a", "#6f6a0c", "#c4bc16", "#ffff23"],
    },
    "light": {
        "panel": "#FAF9F6", "stroke": "#E2E0DA", "grid": "#EDEBE5",
        "text": "#2B2B28", "title": "#0A0A0A", "dim": "#6B6B66",
        "cyan": "#a89f00", "violet": "#989200", "magenta": "#6f6a00", "green": "#a89f00",
        "levels": ["#EDEBE5", "#f1eda6", "#e3df58", "#c9c400", "#a89f00"],
    },
}



# language spectrum: a red ramp plus neutral tones, so the chart stays inside
# the brand instead of turning into a rainbow
PALETTE_DARK = ["#ffff23", "#ffff8a", "#ada614", "#6E6E68", "#4A4A46", "#31312E"]
PALETTE_LIGHT = ["#a89f00", "#d9d500", "#6f6a00", "#6B6B66", "#A8A8A0", "#2B2B28"]


# ------------------------------------------------------------------ fetch ---
def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not t:
        sys.exit("GITHUB_TOKEN / GH_TOKEN is required")
    return t


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "profile-telemetry",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def collect():
    data = gql("""
      query($login:String!) {
        user(login:$login) {
          name login createdAt
          followers { totalCount }
          repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                       privacy:PUBLIC, orderBy:{field:PUSHED_AT, direction:DESC}) {
            totalCount
            nodes { name stargazerCount primaryLanguage { name } }
          }
          contributionsCollection {
            contributionCalendar {
              totalContributions
              weeks { contributionDays { date contributionCount } }
            }
          }
        }
      }""", {"login": USER})["user"]

    days = []
    for week in data["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    days.sort()

    longest = cur = 0
    longest_span = ("", "")
    run_start = None
    for date, count in days:
        if count > 0:
            if run_start is None:
                run_start = date
            cur += 1
            if cur > longest:
                longest = cur
                longest_span = (run_start, date)
        else:
            cur = 0
            run_start = None

    today = dt.date.today()
    tail = [(d, c) for d, c in days if c > 0]
    current, cur_span = 0, ("", "")
    if tail:
        last_date = dt.date.fromisoformat(tail[-1][0])
        if (today - last_date).days <= 1:
            by_date = dict(days)
            cursor = last_date
            while by_date.get(cursor.isoformat(), 0) > 0:
                current += 1
                cursor -= dt.timedelta(days=1)
            cur_span = ((cursor + dt.timedelta(days=1)).isoformat(), last_date.isoformat())

    langs = {}
    for repo in data["repositories"]["nodes"]:
        lang = repo["primaryLanguage"]
        if lang:
            langs[lang["name"]] = langs.get(lang["name"], 0) + 1
    total_langs = sum(langs.values()) or 1
    lang_list = sorted(langs.items(), key=lambda kv: -kv[1])

    return {
        "name": data["name"],
        "login": data["login"],
        "member_since": data["createdAt"][:10],
        "followers": data["followers"]["totalCount"],
        "repos": data["repositories"]["totalCount"],
        "total": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "days": days,
        "current_streak": current,
        "current_span": cur_span,
        "longest_streak": longest,
        "longest_span": longest_span,
        "languages": [(n, c, round(100 * c / total_langs)) for n, c in lang_list],
    }


# ------------------------------------------------------------------ utils ---
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pretty(iso):
    return dt.date.fromisoformat(iso).strftime("%b %-d, %Y") if iso else "—"


def short(iso):
    return dt.date.fromisoformat(iso).strftime("%b %-d") if iso else "—"


def head(w, h, label, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            "<defs>"
            f"<style>text{{font-family:{SANS}}}.num{{font-family:{MONO}}}</style>"
            f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{t["cyan"]}" stop-opacity="0.45"/>'
            f'<stop offset="1" stop-color="{t["cyan"]}" stop-opacity="0.02"/>'
            "</linearGradient></defs>"
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" '
            f'fill="{t["panel"]}" stroke="{t["stroke"]}"/>')


# ------------------------------------------------------------------ panel 1 ---
def telemetry_svg(d, t):
    W, H = 880, 232
    s = [head(W, H, f"{d['total']} total contributions, current streak "
                    f"{d['current_streak']} days, longest streak {d['longest_streak']} days", t)]

    for x in (W / 3, 2 * W / 3):
        s.append(f'<line x1="{x:.0f}" y1="34" x2="{x:.0f}" y2="{H-30}" stroke="{t["stroke"]}"/>')

    cx = W / 6
    s.append(f'<text class="num" x="{cx}" y="98" text-anchor="middle" fill="{t["text"]}" '
             f'font-size="46" font-weight="700">{d["total"]}</text>')
    s.append(f'<text x="{cx}" y="128" text-anchor="middle" fill="{t["dim"]}" '
             f'font-size="13.5" letter-spacing="1.4">TOTAL CONTRIBUTIONS</text>')
    s.append(f'<text x="{cx}" y="154" text-anchor="middle" fill="{t["cyan"]}" '
             f'font-size="11.5">last 12 months · member since '
             f'{dt.date.fromisoformat(d["member_since"]).strftime("%b %Y")}</text>')

    cx = W / 2
    r, cy = 44, 104
    pct = min(1.0, d["current_streak"] / 14) if d["current_streak"] else 0
    circ = 2 * 3.141592653589793 * r
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["stroke"]}" '
             f'stroke-width="6"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["cyan"]}" '
             f'stroke-width="6" stroke-linecap="round" '
             f'stroke-dasharray="{circ*pct:.1f} {circ:.1f}" '
             f'transform="rotate(-90 {cx} {cy})"/>')
    s.append(f'<text class="num" x="{cx}" y="{cy+9}" text-anchor="middle" '
             f'fill="{t["title"]}" font-size="26" font-weight="700">'
             f'{d["current_streak"]}</text>')
    s.append(f'<text x="{cx}" y="{cy+r+24}" text-anchor="middle" fill="{t["cyan"]}" '
             f'font-size="13.5" font-weight="600" letter-spacing="1.4">CURRENT STREAK</text>')
    span = d["current_span"]
    label = f'{short(span[0])} – {short(span[1])}' if span[0] else "start a new streak today"
    s.append(f'<text x="{cx}" y="{cy+r+44}" text-anchor="middle" fill="{t["dim"]}" '
             f'font-size="11.5">{esc(label)}</text>')

    cx = W * 5 / 6
    s.append(f'<text class="num" x="{cx}" y="98" text-anchor="middle" fill="{t["text"]}" '
             f'font-size="46" font-weight="700">{d["longest_streak"]}</text>')
    s.append(f'<text x="{cx}" y="128" text-anchor="middle" fill="{t["dim"]}" '
             f'font-size="13.5" letter-spacing="1.4">LONGEST STREAK</text>')
    span = d["longest_span"]
    label = f'{short(span[0])} – {short(span[1])}' if span[0] else "—"
    s.append(f'<text x="{cx}" y="154" text-anchor="middle" fill="{t["violet"]}" '
             f'font-size="11.5">{esc(label)}</text>')

    s.append(f'<line x1="24" y1="{H-24}" x2="{W-24}" y2="{H-24}" stroke="{t["stroke"]}"/>')
    s.append(f'<text x="24" y="{H-9}" fill="{t["dim"]}" font-size="11">'
             f'@{esc(d["login"])} · {d["repos"]} public repos · '
             f'{d["followers"]} followers · drawn from the GitHub API</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ panel 2 ---
def activity_svg(d, t, span=30):
    W, H = 880, 300
    days = d["days"][-span:]
    s = [head(W, H, f"Daily contribution graph for the last {len(days)} days", t)]

    s.append(f'<text x="{W/2}" y="30" text-anchor="middle" fill="{t["cyan"]}" '
             f'font-size="13.5" font-weight="700" letter-spacing="0.6">'
             f'{esc(d["name"])} ({esc(d["login"])}) · Contribution Graph</text>')

    left, right, top, bottom = 62, W - 30, 52, H - 46
    plot_w, plot_h = right - left, bottom - top
    peak = max(1, max(c for _, c in days))
    step = max(1, round(peak / 4))
    top_val = step * 4

    for i in range(5):
        y = bottom - plot_h * i / 4
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" '
                 f'stroke="{t["grid"]}" stroke-width="1"/>')
        s.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" fill="{t["dim"]}" '
                 f'font-size="10.5" class="num">{step*i}</text>')

    n = len(days)
    pts = [(left + plot_w * (i + 0.5) / n,
            bottom - plot_h * (count / top_val), date, count)
           for i, (date, count) in enumerate(days)]

    area = (f"M{pts[0][0]:.1f},{bottom} L"
            + " L".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
            + f" L{pts[-1][0]:.1f},{bottom} Z")
    s.append(f'<path d="{area}" fill="url(#fade)"><animate attributeName="opacity" '
             f'values="0;0;0.9;0.9" keyTimes="0;0.10;0.55;1" dur="1.9s" begin="0s" '
             f'fill="freeze"/></path>')
    # the line draws itself: dasharray is its own length, so offset 0 (the static
    # base state) already shows the finished line
    length = sum(((pts[i][0]-pts[i-1][0])**2 + (pts[i][1]-pts[i-1][1])**2) ** 0.5
                 for i in range(1, len(pts)))
    s.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
             + f'" fill="none" stroke="{t["cyan"]}" stroke-width="2.2" '
               f'stroke-linejoin="round" stroke-linecap="round" '
               f'stroke-dasharray="{length:.0f}" stroke-dashoffset="0">'
               f'<animate attributeName="stroke-dashoffset" '
               f'values="{length:.0f};0;0" keyTimes="0;0.62;1" dur="1.9s" '
               f'begin="0s" fill="freeze"/></polyline>')

    for i, (x, y, _, count) in enumerate(pts):
        if count > 0:
            k0 = 0.30 + 0.30 * i / max(1, n - 1)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.1" fill="{t["panel"]}" '
                     f'stroke="{t["cyan"]}" stroke-width="1.8">'
                     f'<animate attributeName="opacity" values="0;0;1;1" '
                     f'keyTimes="0;{k0:.3f};{min(0.995, k0 + 0.06):.3f};1" '
                     f'dur="1.9s" begin="0s" fill="freeze"/></circle>')
            if count == peak:
                s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{t["magenta"]}" '
                         f'opacity="0.22"/>')

    for i, (x, _, date, _) in enumerate(pts):
        if i % 5 == 0 or i == n - 1:
            s.append(f'<text x="{x:.1f}" y="{bottom+18}" text-anchor="middle" '
                     f'fill="{t["dim"]}" font-size="10">'
                     f'{dt.date.fromisoformat(date).strftime("%b %-d")}</text>')

    s.append(f'<text x="{left-40}" y="{(top+bottom)/2}" fill="{t["dim"]}" font-size="11" '
             f'transform="rotate(-90 {left-40} {(top+bottom)/2})" text-anchor="middle">'
             f'Contribution Count</text>')
    s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" fill="{t["dim"]}" '
             f'font-size="10.5">Days</text>')

    total = sum(c for _, c in days)
    s.append(f'<text x="{right}" y="30" text-anchor="end" fill="{t["dim"]}" font-size="11">'
             f'{total} in {n} days · peak {peak}</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ panel 3 ---
def languages_svg(d, t, light):
    palette = PALETTE_LIGHT if light else PALETTE_DARK
    W, H = 880, 150
    langs = d["languages"][:6]
    s = [head(W, H, "Language mix across public repositories", t)]
    s.append(f'<text x="24" y="32" fill="{t["title"]}" font-size="13.5" font-weight="700">'
             f'Language Spectrum</text>')
    s.append(f'<text x="{W-24}" y="32" text-anchor="end" fill="{t["dim"]}" font-size="11">'
             f'across {d["repos"]} public repositories</text>')

    bar_x, bar_y, bar_h = 24, 52, 14
    bar_w = W - 48
    total = sum(p for _, _, p in langs) or 1
    x = bar_x
    s.append(f'<clipPath id="barclip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
             f'height="{bar_h}" rx="7"/></clipPath>')
    # the spectrum opens left to right: the mask rect carries the animation, its
    # static width is the finished width
    s.append(f'<mask id="sweep" maskUnits="userSpaceOnUse" x="{bar_x}" y="{bar_y}" '
             f'width="{bar_w}" height="{bar_h}"><rect x="{bar_x}" y="{bar_y}" '
             f'width="{bar_w}" height="{bar_h}" rx="7" fill="#fff">'
             f'<animate attributeName="width" values="0;{bar_w};{bar_w}" '
             f'keyTimes="0;0.55;1" dur="1.4s" begin="0s" fill="freeze"/></rect></mask>')
    s.append('<g clip-path="url(#barclip)" mask="url(#sweep)">')
    for i, (_, _, pct) in enumerate(langs):
        w = bar_w * pct / total
        s.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" '
                 f'fill="{palette[i % len(palette)]}"/>')
        x += w
    s.append("</g>")

    for i, (name, _, pct) in enumerate(langs):
        cx = 24 + (i % 3) * ((W - 48) / 3)
        cy = 96 + (i // 3) * 26
        s.append(f'<circle cx="{cx+5}" cy="{cy}" r="5" fill="{palette[i % len(palette)]}"/>')
        s.append(f'<text x="{cx+18}" y="{cy+4}" fill="{t["text"]}" font-size="12">'
                 f'{esc(name)}</text>')
        s.append(f'<text x="{cx+150}" y="{cy+4}" fill="{t["dim"]}" font-size="11.5" '
                 f'class="num">{pct}%</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ panel 4 ---
def snake_path(left, top, pitch, cell, cols, rows=7):
    """A closed, smoothly-wandering loop through the matrix, plus its length.

    The snake travels right along one wave and back along its mirror image. The
    wave frequency is chosen so both branches land exactly on the middle row at
    the left and right edges, which makes the loop close on itself — no seam for
    the dash pattern to jump across.
    """
    waves = 9
    omega = waves * math.pi / cols
    per_col = 8
    n = cols * per_col

    def branch(sign):
        pts = []
        rng = range(n + 1) if sign > 0 else range(n, -1, -1)
        for k in rng:
            c = k / per_col
            y = 3.0 + sign * 2.55 * math.sin(c * omega)
            y = max(0.3, min(rows - 1.3, y))
            pts.append((left + c * pitch + cell / 2, top + y * pitch + cell / 2))
        return pts

    pts = branch(1) + branch(-1)
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    return d, length


def matrix_svg(d, t):
    days = d["days"]
    cell, gap = 11.5, 3.0
    pitch = cell + gap
    cols = 53
    left, top = 46, 62
    W = left + cols * pitch + 22
    H = int(top + 7 * pitch + 92)

    by_date = dict(days)
    start = dt.date.fromisoformat(days[0][0])
    start -= dt.timedelta(days=start.weekday())
    peak = max(1, max(c for _, c in days))
    levels = t["levels"]

    def level(count):
        if count <= 0:
            return 0
        ratio = count / peak
        return 4 if ratio > 0.66 else 3 if ratio > 0.33 else 2 if ratio > 0.12 else 1

    s = [head(W, H, f"Contribution matrix — {d['total']} contributions over the last year", t)]
    s.append(f'<text x="24" y="32" fill="{t["title"]}" font-size="13.5" font-weight="700">'
             f'Contribution Matrix</text>')
    s.append(f'<text x="{W-24}" y="32" text-anchor="end" fill="{t["dim"]}" font-size="11">'
             f'{d["total"]} contributions · last 12 months</text>')

    seen = set()
    for i in range(cols):
        day = start + dt.timedelta(days=i * 7)
        if day.month not in seen and day.day <= 7:
            seen.add(day.month)
            s.append(f'<text x="{left + i*pitch:.0f}" y="{top-10}" fill="{t["dim"]}" '
                     f'font-size="9.5">{day.strftime("%b")}</text>')

    for wd, label in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
        y = top + wd * pitch + cell - 2
        s.append(f'<text x="{left-10}" y="{y:.0f}" text-anchor="end" fill="{t["dim"]}" '
                 f'font-size="9.5">{label}</text>')

    today = dt.date.today()
    for i in range(cols):
        for wd in range(7):
            day = start + dt.timedelta(days=i * 7 + wd)
            key = day.isoformat()
            if key not in by_date and day > today:
                continue
            count = by_date.get(key, 0)
            lv = level(count)
            extra = (f' stroke="{t["magenta"]}" stroke-width="1" stroke-opacity="0.9"'
                     if lv == 4 else "")
            s.append(f'<rect x="{left + i*pitch:.1f}" y="{top + wd*pitch:.1f}" '
                     f'width="{cell}" height="{cell}" rx="2.5" fill="{levels[lv]}"{extra}>'
                     f'<title>{key}: {count} contribution{"s" if count != 1 else ""}'
                     f'</title></rect>')

    lx = left
    # --------------------------------------------------------------- snake ---
    # One dash travels a closed loop; a shorter, brighter dash sits on its
    # leading edge as the head. Pure CSS, so it animates inside an <img>.
    path_d, plen = snake_path(left, top, pitch, cell, cols)
    body, head_len = 124, 17
    period = plen + body
    dur = period / 62.0
    anim = (f'<animate attributeName="stroke-dashoffset" from="0" '
            f'to="-{period:.1f}" dur="{dur:.1f}s" repeatCount="indefinite"/>')
    s.append(f'<path d="{path_d}" fill="none" stroke="{t["cyan"]}" stroke-width="18" '
             f'stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.15" '
             f'stroke-dasharray="{body + 12} {period - body - 12:.1f}">{anim}</path>')
    s.append(f'<path d="{path_d}" fill="none" stroke="{t["cyan"]}" stroke-width="8" '
             f'stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.88" '
             f'stroke-dasharray="{body} {period - body:.1f}">{anim}</path>')
    # the head is a zero-dash, a gap the length of the body, then a short dash:
    # that puts it exactly on the leading edge instead of the tail
    s.append(f'<path d="{path_d}" fill="none" stroke="{t["violet"]}" stroke-width="12" '
             f'stroke-linecap="round" stroke-linejoin="round" '
             f'stroke-dasharray="0 {body - head_len} {head_len} '
             f'{period - body:.1f}">{anim}</path>')

    ly = top + 7 * pitch + 26
    s.append(f'<text x="{lx}" y="{ly+9}" fill="{t["dim"]}" font-size="10.5">Less</text>')
    lx += 34
    for lv in range(5):
        s.append(f'<rect x="{lx}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" '
                 f'fill="{levels[lv]}"/>')
        lx += pitch
    s.append(f'<text x="{lx+4}" y="{ly+9}" fill="{t["dim"]}" font-size="10.5">More</text>')

    active = sum(1 for _, c in days if c > 0)
    ratio = active / len(days)
    bar_w = W - left - 24
    bar_y = ly + 26
    s.append(f'<rect x="{left}" y="{bar_y}" width="{bar_w}" height="8" rx="4" '
             f'fill="{levels[0]}"/>')
    s.append(f'<rect x="{left}" y="{bar_y}" width="{bar_w*ratio:.1f}" height="8" rx="4" '
             f'fill="{t["cyan"]}" fill-opacity="0.85"/>')
    s.append(f'<text x="{left}" y="{bar_y+26}" fill="{t["dim"]}" font-size="10.5">'
             f'{active} active days · {ratio*100:.0f}% of the year · peak {peak} in one day</text>')
    s.append("</svg>")
    return "".join(s)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()

    out = {}
    for name, t in THEMES.items():
        suffix = "" if name == "dark" else "-light"
        out[f"telemetry{suffix}.svg"] = telemetry_svg(data, t)
        out[f"activity-graph{suffix}.svg"] = activity_svg(data, t)
        out[f"language-spectrum{suffix}.svg"] = languages_svg(data, t, name == "light")
        out[f"contribution-matrix{suffix}.svg"] = matrix_svg(data, t)

    for fname, svg in out.items():
        path = os.path.join(ASSETS, fname)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"assets/{fname} · {len(svg)/1024:.1f} KB")

    with open(os.path.join(ASSETS, "telemetry-data.json"), "w", encoding="utf-8") as fh:
        json.dump({k: v for k, v in data.items() if k != "days"}, fh, indent=2)
    print(f"total={data['total']} current={data['current_streak']} "
          f"longest={data['longest_streak']}")


if __name__ == "__main__":
    main()
