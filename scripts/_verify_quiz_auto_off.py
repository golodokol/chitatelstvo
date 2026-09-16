# -*- coding: utf-8 -*-
from pathlib import Path

root = Path("docs/tilda-zero-main")
for n in [
    "glavnaya.html",
    "00-tilda-zero-upload.html",
    "00-tilda-lite.html",
    "00-tilda-lite-tildacdn.html",
    "_preview-layout.html",
]:
    s = (root / n).read_text(encoding="utf-8")
    i = s.find("chit-quiz-loader")
    chunk = s[i : i + 2800] if i >= 0 else ""
    print("===", n)
    print("has new V", "20260916a" in chunk)
    print("has old V", "20260909m" in chunk)
    print("hash+load()", "location.hash" in chunk and "chitLoadQuiz()" in chunk)
    print("sess auto open", "chit_open_quiz')==='1'" in chunk or 'chit_open_quiz")==="1"' in chunk)
    j = chunk.rfind("})();")
    print("TAIL:", chunk[max(0, j - 280) : j + 5] if j > 0 else chunk[-280:])
    print()

z = (root / "chit-zero.js").read_text(encoding="utf-8")
print("zero: removeItem open_quiz", "chit_open_quiz" in z)
print("zero: LoadQuiz bare on hash", 'chitLoadQuiz()' in z and "#quiz" in z)
# Find hash handling snippet
idx = z.find("#quiz")
print("zero around #quiz:", z[max(0, idx - 80) : idx + 200] if idx >= 0 else "NONE")
