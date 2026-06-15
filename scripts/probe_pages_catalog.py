#!/usr/bin/env python3
import re
import urllib.request

def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": "chit/1"})
    html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", errors="replace")
    print("URL:", url)
    print("  ST205 blocks:", html.count('data-record-type="205"'))
    print("  ST762 blocks:", html.count('data-record-type="762"'))
    print("  Studio Headphones:", html.count("Studio Headphones"))
    print("  previewmode yes:", html.count("previewmode:'yes'"))
    print("  previewmode no:", html.count("previewmode:'no'"))
    print("  storepartuid:", bool(re.search(r"storepartuid", html, re.I)))
    for uid in ["797131986522", "206548598642", "956231952022"]:
        print("  uid", uid, uid in html)
    print()

for path in ["/", "/oplata"]:
    try:
        check("https://chitatelstvo.ru" + path)
    except Exception as exc:
        print("URL:", path, "ERR", exc, "\n")
