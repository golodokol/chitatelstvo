# -*- coding: utf-8 -*-
import time
import urllib.request

time.sleep(1)
url = "https://api.chitatelstvo.ru/assets/chit-quiz.js?v=20260915a&_=%s" % int(time.time())
q = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
print("len", len(q))
print("userActivation", "userActivation" in q)
print("hasQuizIntent", "hasQuizIntent" in q)
print("__chitQuizUserIntent", "__chitQuizUserIntent" in q)
