#!/usr/bin/env bash
# Package Sky Rydahs PWA and publish to dogstar830/sky-rydahs-webxr under /v3/ only. No force push.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${REPO:-dogstar830/sky-rydahs-webxr}"
DEST="${DEST:-/workspace/deploy/sky-rydahs-webxr}"
SUB="${SUB:-v3}"
MSG="${1:-Update v3 PWA test build}"
"$HERE/package_pwa.sh"
for f in index.html manifest.webmanifest sw.js .nojekyll; do [ -e "$HERE/site/$f" ] || { echo "package incomplete: $f" >&2; exit 1; }; done
if [ -d "$DEST/.git" ]; then git -C "$DEST" pull --ff-only origin main
else mkdir -p "$(dirname "$DEST")"; gh repo clone "$REPO" "$DEST"; fi
cd "$DEST"
mkdir -p "$SUB"
rm -rf -- "./$SUB"; mkdir -p "$SUB"; cp -a "$HERE/site/." "$SUB/"   # replaces $SUB only
[ -e .nojekyll ] || touch .nojekyll
git add -- "$SUB" .nojekyll
if git diff --cached --quiet; then echo "No changes."; exit 0; fi
git commit -m "$MSG"
gh auth setup-git; git push origin HEAD:main
echo "Commit: https://github.com/$REPO/commit/$(git rev-parse HEAD)"
