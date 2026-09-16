# -*- coding: utf-8 -*-
import urllib.request

z = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/chit-zero.js?nocache=20260916a", timeout=30
).read()
q = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/chit-quiz.js?nocache=20260916a", timeout=30
).read()
print("zero", len(z))
print("zero removeItem open_quiz", b"removeItem('chit_open_quiz')" in z)
print("zero bare LoadQuiz on hash", b"chitLoadQuiz()" in z and b"hash==='#quiz')window.chitLoadQuiz" in z)
print("quiz openQuizModal hash", b"openQuizModal('hash')" in q)
