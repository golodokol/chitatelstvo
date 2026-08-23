#!/bin/bash
# Lowercase .MP3 extensions in static/early/audio (Linux case-sensitive paths).
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)/static/early/audio"
shopt -s nullglob
for f in "$DIR"/*.MP3; do
  base="${f%.MP3}"
  mv "$f" "${base}.mp3"
done
