# How this profile README works

Every graphic you see on the profile is an SVG committed to this repository and
drawn by a Python script. No badge service, no stats API, no image CDN is
contacted when the page renders — so nothing here can rate-limit, 404, or go
dark because someone else's Vercel deployment fell over.

```
avatar.png ─┐
            ├─► scripts/make_terminal_portrait.py ─► assets/terminal-portrait.svg
            │                                          (animated dot portrait)
GitHub API ─┴─► scripts/make_telemetry.py ──────────► assets/telemetry*.svg
                                                      assets/activity-graph*.svg
                                                      assets/language-spectrum*.svg
                                                      assets/contribution-matrix*.svg
            ┌─► scripts/make_brand_assets.py ───────► assets/hero-banner*.svg
                                                      assets/typing-line*.svg
                                                      assets/footer*.svg
                                                      assets/divider.svg
```

## Refresh everything

```sh
GITHUB_TOKEN=$(gh auth token) ./scripts/refresh.sh
```

Requires Python 3.10+ and Pillow (`pip install -r scripts/requirements.txt`).

## The four pieces

### 1. Dot portrait terminal — `make_terminal_portrait.py`

The avatar is resized to a 48 × 48 grid, quantised to a 14-colour palette, and
every cell above a luminance floor becomes one `<rect>`. Cells are grouped into
12 horizontal bands; each band carries a staggered animation, so the portrait
paints itself top to bottom. A masked
`translateX` reveal types the `neofetch` command, then each readout row fades in.

~1,700 dots, ~93 KB, zero JavaScript.

### 2. Telemetry panels — `make_telemetry.py`

One GraphQL request returns the contribution calendar, repository list and
follower count. From that the script derives the current streak (walking back
from the last active day), the longest streak, the 30-day series, the language
mix, and the 53 × 7 matrix. Everything is emitted twice: dark and `-light`.

The snake on the matrix is one `<path>` stroked with a single dash: the dash is
the body, a shorter brighter dash on the same offset is the head, and animating
`stroke-dashoffset` walks it along the route. The route itself is a closed loop —
a sine wave rightwards, its mirror back — with the frequency picked so both
branches meet exactly on the middle row at both edges, which removes the seam a
straight run would leave when the dash wraps around.

The walk is a SMIL `<animate attributeName="stroke-dashoffset">`, not a CSS
keyframe: see *Motion* below.

### 3. Brand assets — `make_brand_assets.py`

Banner, typing line, footer and divider, again in dark and light. The typing
line cycles four phrases on a 16 s loop. Every phrase shares that one cycle and
owns a 4 s slot inside it: it fades in, its mask slides right to reveal the text
like a caret, then it fades out before the next slot begins. The per-phrase
`keyTimes` are expressed as fractions of the **16 s** cycle (`0 → 0.21 → 0.24`),
not of its own 4 s slot — giving a phrase a 14 s visible window is exactly what
used to stack three phrases on top of each other. Each phrase also carries its
own blinking caret, positioned at that phrase's own text width.

### 4. README — hand written

Each theme graphic is served as a pair of images carrying GitHub's own theme
`<picture>` + `prefers-color-scheme`:

```html
<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/telemetry-light.svg">
  <img src="assets/telemetry.svg" width="100%" alt="...">
</picture>
```

Two alternatives were tried and rejected. The `#gh-dark-mode-only` /
`#gh-light-mode-only` URL fragments only work when GitHub's markdown pipeline
adds the matching class to the element — it does not do that for a plain `<img>`
in a README any more, so both variants render at once. Writing the classes by
hand is the other option, but those classes are legacy. `<picture>` is the form
GitHub actually honours: it resolves against the operating system rather than
the theme picked on github.com, which is a minor cosmetic mismatch at worst and
never a duplicated banner.

## The SIGNAL identity

One visual system covers every asset, defined once per generator in a `THEMES`
dict (`dark` / `light`). The rule is editorial: **ink, paper, and exactly one
accent.**

| Role | Dark | Light |
| --- | --- | --- |
| Background / panel | `#0A0A0A` | `#FFFFFF` / `#FAF9F6` |
| Primary ink | `#FAFAF9` | `#0A0A0A` |
| Accent (the only saturated colour) | `#FF4438` | `#D92B1E` |
| Hairline / stroke | `#242424` | `#E2E0DA` |
| Muted text | `#8A8A85` | `#6B6B66` |

Everything that is not the accent is a neutral step, which is why the language
spectrum is a red ramp plus greys instead of a rainbow, the terminal window
chrome is grey rather than red/amber/green, and the avatar is pressed into a
single ink-to-paper duotone (`MONO_PORTRAIT` in the portrait script) so the red
stays reserved for interface elements. Shaded areas — the contribution matrix,
the activity area fill, the streak ring — all derive from the same accent, so
the page reads as one printed sheet rather than a dashboard.

Editorial furniture is part of the theme too: hairline rules, monospaced micro
labels (`M3T — PROFILE`, `OPEN TO WORK`) and generous letter-spacing on the
display type.

## Conventions

- **Alt text on every image.** The SVGs carry `role="img"` and `aria-label` too.
- **Motion is SMIL.** See below.
- **`-light` suffix** = the variant served in light mode.
- **`assets/archive/`** holds superseded exports. Nothing there is referenced.

## Motion

GitHub serves these files as `<img src="….svg">`, so nothing inside them can run
JavaScript. A `<style>` block *is* honoured by browsers, but not by every
renderer that touches the image — GitHub's image proxy, the mobile app, and
several README viewers either strip it or snapshot the first frame, which is how
the typing line ended up showing all four phrases stacked on top of each other
and the snake sitting still.

Every animation is therefore written with SMIL — `<animate>`,
`<animateTransform>` — which travels with the image itself:

```svg
<animate attributeName="opacity" values="0;1;1;0;0"
         keyTimes="0;0.01;0.21;0.24;1" dur="16s"
         begin="4s" repeatCount="indefinite"/>
```

Two rules follow from that:

1. **The base state of every element is its finished state.** No `opacity="0"`
   on anything that must be visible, no dash offset waiting for an animation to
   reset it. Hiding is only ever used for things that are *supposed* to be hidden
   at rest — phrases 2–4, which each wait their turn. A renderer that ignores
   motion must still produce a complete, readable graphic: one phrase, a full
   snake, a finished portrait.
2. **Timings are absolute fractions of the full cycle.** `keyTimes` on a phrase
   are fractions of the shared 16 s loop, not of that phrase's 4 s slot.

SMIL has no `prefers-reduced-motion` equivalent, so the finished base state is
also the reduced-motion fallback: readers who disable animation get the static
composition, which is why it has to look correct on its own.

### Where the motion is

| Asset | What moves | Technique |
| --- | --- | --- |
| `hero-banner` | the two rule-waves drift in opposite directions, the dot field breathes | `animateTransform` + `animate opacity` |
| `typing-line` | one phrase per 4 s slot, typed by a sliding mask, own caret | `animate opacity` + `animateTransform` |
| `terminal-portrait` | 12 bands paint top to bottom, then 10 readout rows fade in | one shared 3.36 s timeline, `keyTimes` per element |
| `activity-graph` | the line draws itself, the area fades up, the dots pop in left to right | `stroke-dashoffset` + staggered opacity |
| `language-spectrum` | the bar sweeps open left to right | widening mask rect |
| `contribution-matrix` | the snake walks the loop, head and body on one dash | `stroke-dashoffset` |

Everything above shares one trick: the element's attribute is written at its
**finished** value, and the animation is expressed as absolute fractions of a
single timeline starting at `0s`. Nothing waits on a `begin` offset, so nothing
can flash its finished state before its turn.

## Scheduled refresh

`.github/workflows/telemetry.yml` runs daily at 03:17 UTC, regenerates the
assets with the repository's `GITHUB_TOKEN`, and commits them if anything
changed. If the account has a billing hold, the workflow will not start — run
`scripts/refresh.sh` locally and push in that case.
