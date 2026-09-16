# -*- coding: utf-8 -*-
import time
import urllib.request

url = "https://api.chitatelstvo.ru/assets/chit-zero.js?v=20260915a&_=%s" % int(time.time())
z = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
print("len", len(z))
print("markBound", "__chitQuizIntentMarkBound" in z)
print("intent", "__chitQuizUserIntent" in z)
print("remove open", "chit_open_quiz" in z)
