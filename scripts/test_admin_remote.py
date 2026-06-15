#!/usr/bin/env python3
"""Quick admin panel smoke test (run on server)."""
import urllib.parse
import urllib.request
import http.cookiejar

base = "http://127.0.0.1:8000"
password = open("/root/chitatelstvo/.env", encoding="utf-8").read().split("ADMIN_PASSWORD=", 1)[1].split("\n", 1)[0].strip()

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

r1 = opener.open(base + "/admin")
html1 = r1.read().decode("utf-8", errors="replace")
print("GET /admin:", r1.status, "login" if "Пароль" in html1 else "panel")

data = urllib.parse.urlencode({"password": password}).encode()
req = urllib.request.Request(base + "/admin/login", data=data, method="POST")
r2 = opener.open(req)
print("POST /admin/login:", r2.status, r2.geturl())

r3 = opener.open(base + "/admin")
html3 = r3.read().decode("utf-8", errors="replace")
print("GET /admin after login:", r3.status)
if "Панель руководителя" in html3:
    print("OK: panel loaded")
elif "Пароль" in html3:
    print("FAIL: still login page")
else:
    print("UNKNOWN:", html3[:200])
