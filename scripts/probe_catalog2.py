#!/usr/bin/env python3
import json
import urllib.parse
import urllib.request

ORDER_LINKS = [
    ("single", "https://chitatelstvo.ru/#order:" + urllib.parse.quote("Читательство · Разовое") + "=1490"),
    ("self_paced", "https://chitatelstvo.ru/#order:" + urllib.parse.quote("Читательство · Индивидуальное") + "=1990"),
    ("teacher", "https://chitatelstvo.ru/#order:" + urllib.parse.quote("Читательство · С преподавателем") + "=4990"),
]

API_URLS = [
    "https://store.tildaapi.com/api/getproductslist/?recid=2379461281&size=100&getparts=true&flag_root=withroot",
    "https://store.tildaapi.com/api/getproductslist/?recid=2379461281&size=100&getparts=true",
    "https://store.tildaapi.com/api/getstore/?projectid=14447246",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "chit-check/4"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


print("=== Order links for manual/browser test ===")
for name, url in ORDER_LINKS:
    print(name + ":", url)

print("\n=== Tilda store API probes ===")
for url in API_URLS:
    try:
        raw = fetch(url)
        print("\nURL:", url)
        print(raw[:1200])
    except Exception as exc:
        print("\nURL:", url)
        print("ERR:", exc)

html = fetch("https://chitatelstvo.ru/")
print("\n=== Live homepage markers ===")
print("t706__cartdata empty:", "t706__cartdata\"> </div>" in html or "t706__cartdata\"></div>" in html)
for title in ["Читательство · Разовое", "Читательство · Индивидуальное", "Читательство · С преподавателем"]:
    print(title, "in HTML:", title in html)
