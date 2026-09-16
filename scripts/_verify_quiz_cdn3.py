# -*- coding: utf-8 -*-
import urllib.request

q = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/chit-quiz.js?v=20260915a&nocache=20260916b",
    timeout=30,
).read().decode("utf-8", "replace")
z = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/chit-zero.js?v=20260915a&nocache=20260916b",
    timeout=30,
).read().decode("utf-8", "replace")
print("quiz len", len(q))
print("quiz hasQuizIntent", "hasQuizIntent" in q)
print("quiz noteQuizIntent", "noteQuizIntent" in q)
print("quiz openQuizModal hash", "openQuizModal('hash')" in q)
print("zero len", len(z))
print("zero remove open_quiz", "chit_open_quiz" in z and "removeItem" in z)
print("zero LoadQuiz bare", 'chitLoadQuiz()' in z)
