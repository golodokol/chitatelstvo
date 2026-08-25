import re
import subprocess
import urllib.request
from pathlib import Path

URL = (
    "https://api.chitatelstvo.ru/lesson/grade-1-single-lesson-01"
    "?child=e055a673-8f3b-48ae-ab81-e72c78d75c16"
    "&exp=1791222861"
    "&sig=2a1c50e945c4a649d9a971f1f14266dde933184426a2d4d3bdfa3133f856f82a"
)
html = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", errors="replace")
m = re.search(r"<script>\s*([\s\S]*?)\s*</script>\s*</body>", html)
if not m:
    raise SystemExit("script not found")
js = m.group(1)
out = Path(__file__).with_name("_lesson_inline.js")
out.write_text(js, encoding="utf-8")
print("wrote", out, "bytes", len(js))
for cmd in [["node", "--check", str(out)]]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        print("node --check exit", p.returncode)
        if p.stdout:
            print(p.stdout)
        if p.stderr:
            print(p.stderr)
    except FileNotFoundError:
        print("node not found")
