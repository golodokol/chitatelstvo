# -*- coding: utf-8 -*-
import urllib.request
import re

for name in ("chit-zero.js", "chit-quiz.js"):
    raw = urllib.request.urlopen(
        f"https://api.chitatelstvo.ru/assets/{name}?nocache=20260916b", timeout=30
    ).read().decode("utf-8", "replace")
    print("===", name, "len", len(raw))
    print("chit_open_quiz", "chit_open_quiz" in raw)
    print("removeItem", "removeItem" in raw and "chit_open_quiz" in raw)
    print("openQuizModal hash", "openQuizModal('hash')" in raw or 'openQuizModal("hash")' in raw)
    # find auto-open patterns
    for pat in [
        r"chitLoadQuiz\(\)",
        r"openQuizModal\(['\"]hash",
        r"chit_open_quiz['\"]\)===['\"]1",
        r"location\.hash===['\"]#quiz['\"]\)[^;]{0,80}chitLoadQuiz",
    ]:
        m = re.search(pat, raw)
        print("pat", pat, bool(m))
    idx = raw.find("#quiz")
    if idx >= 0:
        print("snippet:", raw[max(0, idx - 60) : idx + 180])
    print()
