#!/usr/bin/env python3
import re, urllib.request

h = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "pay-probe/1"}),
    timeout=30,
).read().decode("utf-8", errors="replace")

idx = h.find("rec2379461281")
block = h[idx:idx+12000] if idx >= 0 else ""

print("=== Payment ===")
for pat, name in [
    (r'data-payment-system="([^"]+)"', "payment_system"),
    (r'data-formactiontype="([^"]+)"', "formactiontype"),
    (r'data-opencart-onorder="([^"]+)"', "opencart_onorder"),
    (r"action='([^']*)'", "form_action"),
]:
    m = re.search(pat, block)
    print(f"  {name}: {m.group(1) if m else '?'}")

print("\n=== Cart / products in HTML ===")
print("  t706__cartdata:", re.search(r"t706__cartdata[^>]*>([^<]*)", block))
print("  products in block:", "product" in block.lower())

print("\n=== Submit button ===")
for m in re.finditer(r't-submit[^>]{0,200}|type="submit"[^>]{0,200}', block):
    print(" ", m.group(0)[:180])

print("\n=== legal_consent in ST100 ===")
print("  field:", "legal_consent" in block)
lc = re.search(r'legal_consent.*?required', block, re.S)
print("  required near:", bool(lc))

print("\n=== chit-zero version ===")
print(re.findall(r"chit-zero\.(js|css)\?v=[^\"']+", h))

print("\n=== Hidden module fields in ST100 ===")
for name in ["module_id", "chosen_stage", "chosen_tale_number"]:
    m = re.search(r'name="' + name + r'"[^>]*value="([^"]*)"', block)
    print(f"  {name} default:", m.group(1) if m else "input found" if name in block else "MISSING")
