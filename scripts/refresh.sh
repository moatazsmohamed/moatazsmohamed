#!/usr/bin/env bash
#
# Rebuilds every generated asset in this profile README.
#
#   GITHUB_TOKEN=... ./scripts/refresh.sh
#
# A token with `read:user` scope is enough: the telemetry panels are read from
# the public GraphQL API. Nothing else needs network access — the banner, the
# typing line, the footer, the divider and the dot portrait are computed here.

set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"

echo "→ brand assets (banner, typing line, footer, divider)"
"$PYTHON" scripts/make_brand_assets.py

echo "→ dot portrait terminal"
"$PYTHON" scripts/make_terminal_portrait.py assets/avatar.png assets/terminal-portrait.svg

echo "→ telemetry panels (needs GITHUB_TOKEN or GH_TOKEN)"
"$PYTHON" scripts/make_telemetry.py

echo "✓ assets refreshed — review with: git diff --stat assets"