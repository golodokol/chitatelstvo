#!/usr/bin/env python3
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"})
html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", errors="replace")

print("js", re.findall(r"chit-zero\.js\?v=([^\"']+)", html))
print("css", re.findall(r"chit-zero\.css\?v=([^\"']+)", html))
print("ST205", html.count('data-record-type="205"'))
print("ST762", html.count('data-record-type="762"'))

for m in re.finditer(r'id="(rec\d+)"[^>]*data-record-type="205"', html):
    print("ST205 rec", m.group(1))

for label in ["Your Name", "Your Email", "Your Phone", "parent_name", "Разовое", "Индивидуальное", "Оплатить"]:
    print(label, label in html)

# form inputs near t706
idx = html.find("t706")
if idx >= 0:
    chunk = html[idx : idx + 15000]
    names = set(re.findall(r'name="([^"]+)"', chunk))
    print("t706 names", sorted(names)[:30])
