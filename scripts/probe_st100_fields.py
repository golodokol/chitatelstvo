#!/usr/bin/env python3
import re
import urllib.request

URL = "https://chitatelstvo.ru/"
req = urllib.request.Request(URL, headers={"User-Agent": "chit-check/5"})
with urllib.request.urlopen(req, timeout=30) as resp:
    html = resp.read().decode("utf-8", errors="replace")

# chit-zero version
for m in re.finditer(r'(https?://[^"\']+chit-zero\.(js|css)\?v=[^"\']+)', html):
    print("asset:", m.group(1))

# ST100 field names
print("\n=== ST100 field names ===")
for m in re.finditer(r'data-field-name="([^"]+)"', html):
    print(" ", m.group(1))

# Select options for notification
print("\n=== notification select values ===")
idx = html.find("notification_channel")
if idx < 0:
    idx = html.find("2811158466360")  # fallback
block = html[max(0, idx - 500) : idx + 3000] if idx >= 0 else ""
for m in re.finditer(r'data-field-value="([^"]+)"', block):
    print(" ", m.group(1))
for m in re.finditer(r'value="(email|telegram|both|web)"', html):
    print(" value:", m.group(1))

# telegram field
print("\n=== telegram/phone field ===")
for pat in ["parent_telegram", "parent_phone", "Номер телефона", "Telegram"]:
    print(f"  {pat}: {pat in html}")

# webhook service id
m = re.search(r'formservices\[\]" value="([^"]+)"', html)
print("\nwebhook service:", m.group(1) if m else "?")

# payment button text
m = re.search(r't706__cartwin-prodamount[^<]{0,200}', html)
print("\npay area snippet exists:", "t706__cartwin" in html)
