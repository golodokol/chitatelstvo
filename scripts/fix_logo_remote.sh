#!/bin/bash
set -euo pipefail
pip3 install -q pillow 2>/dev/null || pip install -q pillow
python3 /tmp/fix_quiz_logo_white.py \
  /var/www/chitatelstvo-assets/logo-chitatelstvo-quiz.png \
  /var/www/chitatelstvo-assets/logo-chitatelstvo-quiz.png
