from pathlib import Path
import urllib.request

js = Path(r"C:\Users\Оля\Documents\Читательство\docs\tilda-zero-main\chit-zero.js").read_text(encoding="utf-8")
print("local 20260823s", "20260823s" in js)
print("local failed attr", "data-chit-img-failed" in js)
print("local print media", "print" in js and "media" in js)

for v in ("20260822k", "20260823s"):
    url = f"https://api.chitatelstvo.ru/assets/chit-zero.js?v={v}&_={v}"
    text = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    print(v, "len", len(text), "has safari", "20260823s" in text, "has hide", "data-chit-img-failed" in text)
