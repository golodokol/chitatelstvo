# -*- coding: utf-8 -*-
import re
import urllib.request

html = urllib.request.urlopen("https://chitatelstvo.ru/", timeout=30).read().decode(
    "utf-8", "replace"
)
print("len", len(html))
print("CHIT_QUIZ_AUTO", re.findall(r"CHIT_QUIZ_AUTO=\{[^}]+\}", html)[:5])
print(
    "zero versions",
    sorted(set(re.findall(r"chit-zero\.js\?v=([^\"'\s&]+)", html))),
)
print(
    "quiz versions",
    sorted(set(re.findall(r"chit-quiz\.js\?v=([^\"'\s&]+)", html))),
)
for pat in [
    "chitLoadQuiz()",
    "chit_open_quiz')==='1'",
    'chit_open_quiz")==="1"',
    "openQuizModal('hash')",
    "hash==='#quiz'",
]:
    print(pat, html.count(pat))
i = html.find("chit-quiz-loader")
chunk = html[i : i + 3200] if i >= 0 else ""
print("has loader", i >= 0)
print("loader LoadQuiz bare", "chitLoadQuiz()" in chunk)
print("loader replaceState", "replaceState" in chunk)
j = chunk.rfind("})();")
print("loader tail:", chunk[max(0, j - 320) : j + 5] if j > 0 else chunk[-320:])
