#!/usr/bin/env python3
"""
Builds the self-hosted "Live Telemetry" panels for the profile README:

  assets/telemetry.svg            total contributions · current streak · longest streak
  assets/activity-graph.svg       daily contributions, last 30 days
  assets/language-spectrum.svg    language mix across public repositories

Everything is drawn locally from the GitHub API, so the README never depends on
a third-party stats service that can rate-limit or go down.

Auth: GITHUB_TOKEN (or GH_TOKEN) in the environment.
Usage: python3 scripts/make_telemetry.py
"""

import datetime as dt
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")
USER = "moatazsmohamed"

BG = "#0D1117"
PANEL = "#0B0F14"
STROKE = "#21262D"
GRIDC = "#1B222B"
CYAN = "#22D3EE"
MAGENTA = "#E879F9"
VIOLET = "#8B5CF6"
GREEN = "#3FB950"
DIM = "#8B949E"
TEXT = "#C9D1D9"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Segoe UI',Ubuntu,-apple-system,Helvetica,Arial,sans-serif"


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


def rest(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"bearer {token()}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "profile-telemetry"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def collect():
    data = gql("""
      query($login:String!) {
        user(login:$login) {
          name login
          followers { totalCount }
          repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                       privacy:PUBLIC, orderBy:{field:PUSHED_AT, direction:DESC}) {
            totalCount
            nodes { name stargazerCount primaryLanguage { name color } }
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

    # streaks
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

    # current streak counts back from the most recent active day (today or
    # yesterday, so an unfinished day does not break it)
    today = dt.date.today()
    tail = [(d, c) for d, c in days if c > 0]
    current, cur_span = 0, ("", "")
    if tail:
        last_date = dt.date.fromisoformat(tail[-1][0])
        if (today - last_date).days <= 1:
            current = 0
            idx = len(days) - 1
            # walk backwards over calendar days
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
        "followers": data["followers"]["totalCount"],
        "repos": data["repositories"]["totalCount"],
        "total": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "first": days[0][0] if days else "",
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
    if not iso:
        return "—"
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b %-d, %Y") if os.name != "nt" else d.strftime("%b %d, %Y")


def short(iso):
    if not iso:
        return "—"
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b %-d") if os.name != "nt" else d.strftime("%b %d")


def head(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            "<defs>"
            f"<style>text{{font-family:{SANS}}}.num{{font-family:{MONO}}}"
            "</style>"
            f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.45"/>'
            f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0.02"/>'
            "</linearGradient></defs>"
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" '
            f'fill="{PANEL}" stroke="{STROKE}"/>')


# ------------------------------------------------------------------ panel 1 ---
def telemetry_svg(d):
    W, H = 880, 232
    s = [head(W, H, f"{d['total']} total contributions, current streak "
                    f"{d['current_streak']} days, longest streak {d['longest_streak']} days")]

    cols = [W / 3, 2 * W / 3]
    for x in cols:
        s.append(f'<line x1="{x:.0f}" y1="34" x2="{x:.0f}" y2="{H-30}" '
                 f'stroke="{STROKE}"/>')

    # --- total contributions
    cx = W / 6
    s.append(f'<text class="num" x="{cx}" y="98" text-anchor="middle" fill="{TEXT}" '
             f'font-size="46" font-weight="700">{d["total"]}</text>')
    s.append(f'<text x="{cx}" y="128" text-anchor="middle" fill="{DIM}" '
             f'font-size="13.5" letter-spacing="1.4">TOTAL CONTRIBUTIONS</text>')
    s.append(f'<text x="{cx}" y="154" text-anchor="middle" fill="{CYAN}" '
             f'font-size="11.5">{esc(pretty(d["first"]))} – Present</text>')

    # --- current streak with ring
    cx = W / 2
    r = 44
    cy = 104
    pct = min(1.0, d["current_streak"] / 14) if d["current_streak"] else 0
    circ = 2 * 3.141592653589793 * r
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{STROKE}" '
             f'stroke-width="6"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CYAN}" '
             f'stroke-width="6" stroke-linecap="round" '
             f'stroke-dasharray="{circ*pct:.1f} {circ:.1f}" '
             f'transform="rotate(-90 {cx} {cy})"/>')
    s.append(f'<text class="num" x="{cx}" y="{cy+9}" text-anchor="middle" '
             f'fill="{MAGENTA}" font-size="26" font-weight="700">'
             f'{d["current_streak"]}</text>')
    s.append(f'<text x="{cx}" y="{cy+r+24}" text-anchor="middle" fill="{CYAN}" '
             f'font-size="13.5" font-weight="600" letter-spacing="1.4">CURRENT STREAK</text>')
    span = d["current_span"]
    label = f'{short(span[0])} – {short(span[1])}' if span[0] else "start a new streak today"
    s.append(f'<text x="{cx}" y="{cy+r+44}" text-anchor="middle" fill="{DIM}" '
             f'font-size="11.5">{esc(label)}</text>')

    # --- longest streak
    cx = W * 5 / 6
    s.append(f'<text class="num" x="{cx}" y="98" text-anchor="middle" fill="{TEXT}" '
             f'font-size="46" font-weight="700">{d["longest_streak"]}</text>')
    s.append(f'<text x="{cx}" y="128" text-anchor="middle" fill="{DIM}" '
             f'font-size="13.5" letter-spacing="1.4">LONGEST STREAK</text>')
    span = d["longest_span"]
    label = f'{short(span[0])} – {short(span[1])}' if span[0] else "—"
    s.append(f'<text x="{cx}" y="154" text-anchor="middle" fill="{VIOLET}" '
             f'font-size="11.5">{esc(label)}</text>')

    # footer
    s.append(f'<line x1="24" y1="{H-24}" x2="{W-24}" y2="{H-24}" stroke="{STROKE}"/>')
    s.append(f'<text x="24" y="{H-9}" fill="{DIM}" font-size="11">'
             f'@{esc(d["login"])} · {d["repos"]} public repos · '
             f'{d["followers"]} followers · refreshed daily by GitHub Actions</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ panel 2 ---
def activity_svg(d, span=30):
    W, H = 880, 300
    days = d["days"][-span:]
    s = [head(W, H, f"Daily contribution graph for the last {len(days)} days")]

    s.append(f'<text x="{W/2}" y="30" text-anchor="middle" fill="{CYAN}" '
             f'font-size="13.5" font-weight="700" letter-spacing="0.6">'
             f'{esc(d["name"])} ({esc(d["login"])}) · Contribution Graph</text>')

    left, right, top, bottom = 62, W - 30, 52, H - 46
    plot_w = right - left
    plot_h = bottom - top
    peak = max(1, max(c for _, c in days))
    # round the axis up to a friendly number
    step = max(1, round(peak / 4))
    top_val = step * 4

    for i in range(5):
        y = bottom - plot_h * i / 4
        val = step * i
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" '
                 f'stroke="{GRIDC}" stroke-width="1"/>')
        s.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" fill="{DIM}" '
                 f'font-size="10.5" class="num">{val}</text>')

    n = len(days)
    pts = []
    for i, (date, count) in enumerate(days):
        x = left + (plot_w * (i + 0.5) / n)
        y = bottom - plot_h * (count / top_val)
        pts.append((x, y, date, count))

    line = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
    area = (f"M{pts[0][0]:.1f},{bottom} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
            + f" L{pts[-1][0]:.1f},{bottom} Z")

    s.append(f'<path d="{area}" fill="url(#fade)"/>')
    s.append(f'<polyline points="{line}" fill="none" stroke="{CYAN}" stroke-width="2.2" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')

    for i, (x, y, date, count) in enumerate(pts):
        if count > 0:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.1" fill="{BG}" '
                     f'stroke="{CYAN}" stroke-width="1.8"/>')
            if count == peak:
                s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{MAGENTA}" '
                         f'opacity="0.22"/>')

    for i, (x, y, date, count) in enumerate(pts):
        if i % 5 == 0 or i == n - 1:
            dd = dt.date.fromisoformat(date)
            s.append(f'<text x="{x:.1f}" y="{bottom+18}" text-anchor="middle" '
                     f'fill="{DIM}" font-size="10">{dd.strftime("%b %-d")}</text>')

    s.append(f'<text x="{left-40}" y="{(top+bottom)/2}" fill="{DIM}" font-size="11" '
             f'transform="rotate(-90 {left-40} {(top+bottom)/2})" text-anchor="middle">'
             f'Contribution Count</text>')
    s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" fill="{DIM}" '
             f'font-size="10.5">Days</text>')

    total = sum(c for _, c in days)
    s.append(f'<text x="{right}" y="30" text-anchor="end" fill="{DIM}" font-size="11">'
             f'{total} in {n} days · peak {peak}</text>')
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ panel 3 ---
PALETTE = [CYAN, VIOLET, MAGENTA, GREEN, "#F59E0B", "#F472B6", "#38BDF8", "#A3E635"]


def languages_svg(d):
    W, H = 880, 150
    langs = d["languages"][:6]
    s = [head(W, H, "Language mix across public repositories")]
    s.append(f'<text x="24" y="32" fill="{TEXT}" font-size="13.5" font-weight="700">'
             f'Language Spectrum</text>')
    s.append(f'<text x="{W-24}" y="32" text-anchor="end" fill="{DIM}" font-size="11">'
             f'across {d["repos"]} public repositories</text>')

    bar_x, bar_y, bar_h = 24, 52, 14
    bar_w = W - 48
    total = sum(p for _, _, p in langs) or 1
    x = bar_x
    s.append(f'<clipPath id="barclip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
             f'height="{bar_h}" rx="7"/></clipPath>')
    s.append('<g clip-path="url(#barclip)">')
    for i, (name, count, pct) in enumerate(langs):
        w = bar_w * pct / total
        s.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" '
                 f'fill="{PALETTE[i % len(PALETTE)]}"/>')
        x += w
    s.append("</g>")

    lx, ly = 24, 96
    for i, (name, count, pct) in enumerate(langs):
        col = i % 3
        row = i // 3
        cx = lx + col * ((W - 48) / 3)
        cy = ly + row * 26
        s.append(f'<circle cx="{cx+5}" cy="{cy}" r="5" fill="{PALETTE[i % len(PALETTE)]}"/>')
        s.append(f'<text x="{cx+18}" y="{cy+4}" fill="{TEXT}" font-size="12">'
                 f'{esc(name)}</text>')
        s.append(f'<text x="{cx+150}" y="{cy+4}" fill="{DIM}" font-size="11.5" '
                 f'class="num">{pct}%</text>')
    s.append("</svg>")
    return "".join(s)


LEVELS = ["#161B22", "#0E4F5C", "#127C8C", "#17A9BF", CYAN]


def matrix_svg(d):
    """A 53x7 pixel matrix of the contribution year, plus a progress bar."""
    days = d["days"]
    cell, gap = 11.5, 3.0
    pitch = cell + gap
    cols = 53
    left, top = 46, 62
    W = left + cols * pitch + 22
    grid_h = 7 * pitch
    H = int(top + grid_h + 92)

    by_date = {date: count for date, count in days}
    start = dt.date.fromisoformat(days[0][0])
    start -= dt.timedelta(days=(start.weekday()))
    peak = max(1, max(c for _, c in days))

    def level(count):
        if count <= 0:
            return 0
        ratio = count / peak
        if ratio > 0.66:
            return 4
        if ratio > 0.33:
            return 3
        if ratio > 0.12:
            return 2
        return 1

    s = [head(W, H, f"Contribution matrix — {d['total']} contributions over the last year")]
    s.append(f'<text x="24" y="32" fill="{TEXT}" font-size="13.5" font-weight="700">'
             f'Contribution Matrix</text>')
    s.append(f'<text x="{W-24}" y="32" text-anchor="end" fill="{DIM}" font-size="11">'
             f'{d["total"]} contributions · last 12 months</text>')

    # month labels
    seen = set()
    for i in range(cols):
        day = start + dt.timedelta(days=i * 7)
        if day.month not in seen and day.day <= 7:
            seen.add(day.month)
            x = left + i * pitch
            s.append(f'<text x="{x:.0f}" y="{top-10}" fill="{DIM}" font-size="9.5">'
                     f'{day.strftime("%b")}</text>')

    for wd, label in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
        y = top + wd * pitch + cell - 2
        s.append(f'<text x="{left-10}" y="{y:.0f}" text-anchor="end" fill="{DIM}" '
                 f'font-size="9.5">{label}</text>')

    for i in range(cols):
        for wd in range(7):
            day = start + dt.timedelta(days=i * 7 + wd)
            key = day.isoformat()
            if key not in by_date and day > dt.date.today():
                continue
            count = by_date.get(key, 0)
            lv = level(count)
            x = left + i * pitch
            y = top + wd * pitch
            fill = LEVELS[lv]
            extra = ""
            if lv == 4:
                extra = f' stroke="{MAGENTA}" stroke-width="1" stroke-opacity="0.9"'
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" '
                     f'rx="2.5" fill="{fill}"{extra}><title>{key}: {count} '
                     f'contribution{"s" if count != 1 else ""}</title></rect>')

    # legend
    lx = left
    ly = top + grid_h + 26
    s.append(f'<text x="{lx}" y="{ly+9}" fill="{DIM}" font-size="10.5">Less</text>')
    lx += 34
    for lv in range(5):
        s.append(f'<rect x="{lx}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" '
                 f'fill="{LEVELS[lv]}"/>')
        lx += pitch
    s.append(f'<text x="{lx+4}" y="{ly+9}" fill="{DIM}" font-size="10.5">More</text>')

    # active-day progress bar
    active = sum(1 for _, c in days if c > 0)
    ratio = active / len(days)
    bar_x, bar_w = left, W - left - 24
    bar_y = ly + 26
    s.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="8" rx="4" '
             f'fill="{LEVELS[0]}"/>')
    s.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w*ratio:.1f}" height="8" '
             f'rx="4" fill="{CYAN}" fill-opacity="0.85"/>')
    s.append(f'<text x="{bar_x}" y="{bar_y+26}" fill="{DIM}" font-size="10.5">'
             f'{active} active days · {ratio*100:.0f}% of the year · peak {peak} in one day</text>')

    s.append("</svg>")
    return "".join(s)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    data = collect()
    out = {
        "telemetry.svg": telemetry_svg(data),
        "activity-graph.svg": activity_svg(data),
        "language-spectrum.svg": languages_svg(data),
        "contribution-matrix.svg": matrix_svg(data),
    }
    for name, svg in out.items():
        path = os.path.join(ASSETS, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"{path} · {len(svg)/1024:.1f} KB")
    with open(os.path.join(ASSETS, "telemetry-data.json"), "w", encoding="utf-8") as fh:
        json.dump({k: v for k, v in data.items() if k != "days"}, fh, indent=2)
    print(f"total={data['total']} current={data['current_streak']} "
          f"longest={data['longest_streak']}")


if __name__ == "__main__":
    main()
