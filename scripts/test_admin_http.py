#!/usr/bin/env python3
import urllib.parse
import urllib.request
import http.cookiejar

password = open("/root/chitatelstvo/.env", encoding="utf-8").read().split("ADMIN_PASSWORD=", 1)[1].split("\n", 1)[0].strip()
base = "http://api.chitatelstvo.ru"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

data = urllib.parse.urlencode({"password": password}).encode()
req = urllib.request.Request(base + "/admin/login", data=data, method="POST")
opener.open(req)
print("cookies after http login:", [(c.name, c.secure) for c in jar])

r3 = opener.open(base + "/admin")
html3 = r3.read().decode("utf-8", errors="replace")
print("after login on http:", "panel" if "Панель" in html3 else "login")
