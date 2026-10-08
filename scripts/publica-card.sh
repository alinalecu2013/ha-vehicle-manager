#!/usr/bin/env bash
# Publica cardul in depozitul HACS separat (alinalecu2013/vehicle-manager-card).
#
# Sursa cardului ramane in acest depozit; scriptul copiaza fisierul in clona
# depozitului cardului (implicit ../vehicle-manager-card), face commit, push si
# un release cu aceeasi versiune ca CARD_VERSION.
#
# Utilizare: scripts/publica-card.sh [cale-clona-card]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CARD_DIR="${1:-$ROOT/../vehicle-manager-card}"
SOURCE="$ROOT/custom_components/vehicle_manager/www/vehicle-manager-card.js"
REPO="alinalecu2013/vehicle-manager-card"
GH="${GH:-gh}"
command -v "$GH" >/dev/null 2>&1 || GH="/c/Program Files/GitHub CLI/gh.exe"

VERSION="$(sed -n 's/^const CARD_VERSION = "\(.*\)";$/\1/p' "$SOURCE")"
MANIFEST_VERSION="$(sed -n 's/.*"version": "\(.*\)".*/\1/p' "$ROOT/custom_components/vehicle_manager/manifest.json")"

if [ -z "$VERSION" ]; then
  echo "Nu gasesc CARD_VERSION in $SOURCE" >&2
  exit 1
fi
if [ "$VERSION" != "$MANIFEST_VERSION" ]; then
  echo "CARD_VERSION ($VERSION) difera de versiunea din manifest.json ($MANIFEST_VERSION)" >&2
  exit 1
fi
if [ ! -d "$CARD_DIR/.git" ]; then
  echo "Nu gasesc clona depozitului cardului in $CARD_DIR" >&2
  exit 1
fi

cp "$SOURCE" "$CARD_DIR/vehicle-manager-card.js"
cd "$CARD_DIR"

if git diff --quiet && git diff --cached --quiet; then
  echo "Cardul din $CARD_DIR este deja la zi."
else
  git add vehicle-manager-card.js
  git commit -q -m "Vehicle Manager Card $VERSION"
  git push -q
  echo "Cardul $VERSION a fost urcat."
fi

if "$GH" release view "v$VERSION" -R "$REPO" >/dev/null 2>&1; then
  echo "Release-ul v$VERSION exista deja."
else
  "$GH" release create "v$VERSION" -R "$REPO" --target main --title "v$VERSION" \
    --notes "Cardul pentru Vehicle Manager $VERSION. Detalii: https://github.com/alinalecu2013/ha-vehicle-manager/releases/tag/v$VERSION"
fi
