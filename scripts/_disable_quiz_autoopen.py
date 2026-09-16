# -*- coding: utf-8 -*-
"""Strip quiz auto-open from inline loaders in homepage HTML sources."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "docs" / "tilda-zero-main"
NEW_V = "20260916a"

# Auto-open via hash: load+open quiz
HASH_OPEN = re.compile(
    r"if\s*\(\s*location\.hash\s*===\s*['\"]#quiz['\"]\s*\)\s*"
    r"window\.chitLoadQuiz\s*\(\s*\)\s*;?"
)

# Clear hash only (no open) — keep as-is if already present, else replace hash-open
HASH_CLEAR = (
    "if(location.hash==='#quiz'){"
    "try{history.replaceState(null,'',location.pathname+location.search);}"
    "catch(err){location.hash='';}}"
)

# sessionStorage auto-open block (minified one-liner variants)
SESS_OPEN = re.compile(
    r"try\s*\{\s*"
    r"if\s*\(\s*sessionStorage\.getItem\(['\"]chit_open_quiz['\"]\)\s*===\s*['\"]1['\"]\s*\)\s*\{\s*"
    r"sessionStorage\.removeItem\(['\"]chit_open_quiz['\"]\)\s*;\s*"
    r"window\.chitLoadQuiz\s*\(\s*function\s*\(\s*\)\s*\{[^}]*\}\s*\)\s*;?\s*"
    r"\}\s*"
    r"\}\s*catch\s*\([^)]*\)\s*\{\s*\}\s*",
    re.S,
)

SESS_CLEAR = "try{sessionStorage.removeItem('chit_open_quiz');}catch(err){}"

# Also catch non-minified / slightly different openReady callbacks
SESS_OPEN2 = re.compile(
    r"try\s*\{\s*"
    r"if\s*\(\s*sessionStorage\.getItem\(['\"]chit_open_quiz['\"]\)\s*===\s*['\"]1['\"]\s*\)\s*\{"
    r"[\s\S]*?"
    r"\}\s*"
    r"\}\s*catch\s*\([^)]*\)\s*\{\s*\}\s*",
)

files = [
    ROOT / "glavnaya.html",
    ROOT / "_preview-layout.html",
    ROOT / "00-tilda-zero-upload.html",
    ROOT / "00-tilda-lite.html",
    ROOT / "00-tilda-lite-tildacdn.html",
]

for path in files:
    if not path.exists():
        print("SKIP missing", path.name)
        continue
    text = path.read_text(encoding="utf-8")
    orig = text

    text, n1 = HASH_OPEN.subn(HASH_CLEAR, text)
    text, n2 = SESS_OPEN.subn(SESS_CLEAR, text)
    # only if still has auto-load via chit_open_quiz
    if "chit_open_quiz" in text and "chitLoadQuiz(function" in text:
        text, n3 = SESS_OPEN2.subn(SESS_CLEAR, text)
    else:
        n3 = 0

    # bump cache-bust version in quiz loader
    text = re.sub(
        r'(id="chit-quiz-loader"[\s\S]{0,400}?V\s*=\s*")[^"]+(")',
        rf"\g<1>{NEW_V}\2",
        text,
        count=1,
    )
    # also simple V= patterns near chit-quiz
    text = text.replace('V="20260909m"', f'V="{NEW_V}"')
    text = text.replace("V='20260909m'", f"V='{NEW_V}'")

    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"patched {path.name}: hash={n1} sess={n2}+{n3}")
    else:
        still = "chit_open_quiz" in text and "chitLoadQuiz" in text
        print(f"unchanged {path.name} still_auto={still}")
