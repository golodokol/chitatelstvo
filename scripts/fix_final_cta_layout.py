#!/usr/bin/env python3
"""Patch final-cta layout in chit-zero.css: no sticky scroll gap, restore CTA bg URL."""
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "docs/tilda-zero-main/chit-zero.css"
text = CSS.read_text(encoding="utf-8")

OLD_CTA = "https://static.tildacdn.com/tild6364-6633-4361-a235-313532333937/cta-fairy-tale-bg.PNG"
NEW_CTA = "https://static.tildacdn.com/tild3031-3135-4034-b763-653465363865/cta-fairy-tale-bg.webp"
text = text.replace(OLD_CTA, NEW_CTA)

replacements = [
    (".final-cta-scroller{height:max(135vh,1020px);", ".final-cta-scroller{height:auto;"),
    (".final-cta{position:sticky;top:0;height:100vh;", ".final-cta{position:relative;top:auto;height:auto;"),
    ("@media (max-width:768px){.final-cta-scroller{height:max(120vh,860px);}", "@media (max-width:768px){.final-cta-scroller{height:auto;}"),
    ("@media (max-width:560px){.final-cta-scroller{height:max(115vh,780px);}", "@media (max-width:560px){.final-cta-scroller{height:auto;}"),
]
for old, new in replacements:
    if old not in text:
        print("WARN missing:", old[:60])
    text = text.replace(old, new)

CSS.write_text(text, encoding="utf-8")
print("patched", CSS)
