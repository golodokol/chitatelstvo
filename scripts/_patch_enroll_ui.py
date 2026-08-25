#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
css_path = DIR / "chit-zero.css"
txt_path = DIR / "02-css.txt"
css = css_path.read_text(encoding="utf-8")

old_active = """    .enroll-opt.pill.is-active {
      box-shadow: 0 6px 18px rgba(91, 127, 166, 0.22);
    }"""
new_active = """    .enroll-opt.pill.is-active {
      box-shadow: 0 6px 18px rgba(91, 127, 166, 0.22);
      background: var(--blue) !important;
      border-color: var(--blue) !important;
      color: #fff !important;
      -webkit-text-fill-color: #fff !important;
    }
    .enroll-opt.pill.is-active .enroll-opt__name,
    .enroll-opt.pill.is-active .enroll-opt__meta {
      color: #fff !important;
      -webkit-text-fill-color: #fff !important;
    }"""
if old_active in css and "enroll-opt.pill.is-active .enroll-opt__name" not in css:
    css = css.replace(old_active, new_active, 1)

old_sum = """    .summary {
      background: var(--accent-pale); border-radius: 12px;
      padding: 18px 24px; font-size: 22px; min-height: 56px;
      border: 1.5px dashed var(--accent);
      font-family: var(--hand); font-weight: 600;
      line-height: 1.45;
      color: var(--text-warm);
    }
    .summary.is-empty {
      display: flex; align-items: center; justify-content: center;
      text-align: center;
    }"""
new_sum = """    .summary {
      background: var(--accent-pale); border-radius: 12px;
      padding: 18px 24px; font-size: 22px; min-height: 56px;
      border: 1.5px solid rgba(143, 125, 163, 0.35);
      font-family: var(--hand); font-weight: 600;
      line-height: 1.45;
      color: var(--text-warm);
    }
    .summary.is-empty {
      display: flex; align-items: center; justify-content: center;
      text-align: center;
      border-style: dashed;
      background: #fff;
    }"""
if old_sum in css:
    css = css.replace(old_sum, new_sum, 1)

# tale-btn active
css = re.sub(
    r"\.tale-btn\.is-active \{ border-color: var\(--blue\); background: var\(--accent-pale\); \}\s*"
    r"\.tale-num \{[^}]+\}\s*"
    r"\.tale-btn\.is-active \.tale-num \{ background: var\(--blue\); color: #fff; \}",
    ".tale-btn.is-active {\n"
    "      border-color: var(--blue) !important;\n"
    "      background: var(--blue-pale) !important;\n"
    "      box-shadow: 0 0 0 2px rgba(91, 127, 166, 0.25);\n"
    "    }\n"
    "    .tale-num {\n"
    "      display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center;\n"
    "      border-radius: 50%; background: var(--blue-pale); font-size: 13px;\n"
    "      font-weight: 800; margin-right: 8px; color: var(--blue);\n"
    "    }\n"
    "    .tale-btn.is-active .tale-num {\n"
    "      background: var(--blue) !important;\n"
    "      color: #fff !important;\n"
    "      -webkit-text-fill-color: #fff !important;\n"
    "    }",
    css,
    count=1,
)

css_path.write_text(css, encoding="utf-8")
txt_path.write_text(css, encoding="utf-8")

bp = ROOT / "scripts" / "build_tilda_upload.py"
bp.write_text(
    re.sub(r'VERSION = "[^"]+"', 'VERSION = "20260823t"', bp.read_text(encoding="utf-8"), count=1),
    encoding="utf-8",
)
print("css patched", "enroll-opt__name" in css, "border-style: dashed" in css)
print("version -> 20260823t")
