import re
import urllib.request

URL = (
    "https://api.chitatelstvo.ru/lesson/grade-1-single-lesson-01"
    "?child=e055a673-8f3b-48ae-ab81-e72c78d75c16"
    "&exp=1791222861"
    "&sig=2a1c50e945c4a649d9a971f1f14266dde933184426a2d4d3bdfa3133f856f82a"
)
html = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8", errors="replace")
print("status ok, len", len(html))
for name in ["lesson_slovik.js", "emotion_wheel.js", "lesson_quiz.js", "chit-student.css"]:
    m = re.search(r"/static/" + re.escape(name) + r"\?v=([^\"']+)", html)
    print(name, m.group(1) if m else "MISSING")
scripts = re.findall(r'<script src="([^"]+)"', html)
print("external scripts:", scripts)
print("has emotion block", "step-emotion" in html)
print("btn disabled attr", 'id="btn-emotion" disabled' in html)
# progress url
m = re.search(r'progress_url[^"]*"([^"]+)"', html)
print("progress in page", "progress" in html[:5000])
# fetch static js sizes
for s in scripts:
    try:
        data = urllib.request.urlopen("https://api.chitatelstvo.ru" + s.split("?", 1)[0], timeout=20)
        body = data.read()
        print("asset", s, "status", data.status, "bytes", len(body))
    except Exception as e:
        print("asset FAIL", s, e)
