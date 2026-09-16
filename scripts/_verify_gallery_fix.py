# -*- coding: utf-8 -*-
import urllib.request

c = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/course-pages/course-lite.css?nocache=i2",
    timeout=30,
).read().decode("utf-8", "replace")
i = c.find(".ccl-lessons li")
print("css snippet:", c[i : i + 140])
print("toggle center:", ".ccl-lesson__toggle" in c and "align-items: center" in c[c.find(".ccl-lesson__toggle") : c.find(".ccl-lesson__toggle") + 200])

d = urllib.request.urlopen(
    "https://api.chitatelstvo.ru/assets/course-pages/course-lite-data.js?nocache=i2",
    timeout=30,
).read().decode("utf-8", "replace")
print("has platform frames title", "Ещё кадры с платформы" in d)
print("gallery count", d.count('"gallery"'))
