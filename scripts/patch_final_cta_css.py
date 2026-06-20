#!/usr/bin/env python3
import re
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "docs/tilda-zero-main/chit-zero.css"
text = CSS.read_text(encoding="utf-8")

CTA_URL = "https://static.tildacdn.com/tild3031-3135-4034-b763-653465363865/cta-fairy-tale-bg.webp"

new_block = (
    ".final-cta-scroller{height:max(135vh,1020px);background:none;}"
    ".final-cta{position:sticky;top:0;height:100vh;min-height:760px;text-align:center;"
    "padding:48px 8% 64px 24px;display:flex;align-items:center;justify-content:flex-end;overflow:hidden;}"
    f".final-cta__bg{{position:absolute;inset:0;z-index:0;background:url('{CTA_URL}') center/cover no-repeat;transform:scale(1.02);}}"
    ".final-cta__bg::after{content:'';position:absolute;inset:0;"
    "background:linear-gradient(105deg,rgba(18,26,44,0.12) 0%,rgba(18,26,44,0.02) 42%,rgba(18,26,44,0.38) 100%);pointer-events:none;}"
    ".final-cta__frame{position:relative;z-index:1;max-width:440px;width:100%;margin-left:auto;"
    "background:rgba(255,252,248,0.94);border:2px solid rgba(255,255,255,0.9);border-radius:22px;"
    "padding:44px 40px 40px;box-shadow:0 20px 56px rgba(12,22,42,0.28);backdrop-filter:blur(8px);"
    "opacity:1;transform:none;transition:opacity .75s ease,transform .75s cubic-bezier(.22,1,.36,1);}"
    ".final-cta.is-active .final-cta__frame{opacity:1;transform:translateX(0);}"
    "@media (max-width:768px){.final-cta-scroller{height:max(120vh,860px);}"
    ".final-cta{position:relative;min-height:620px;padding:48px 20px 56px;justify-content:center;align-items:flex-start;}"
    ".final-cta__frame{max-width:100%;margin-left:0;}}"
    "@media (max-width:560px){.final-cta-scroller{height:max(115vh,780px);}.final-cta{min-height:540px;}"
    ".final-cta__frame{padding:28px 24px 24px;}}"
    "@media (prefers-reduced-motion:reduce){.final-cta-scroller{height:auto;}"
    ".final-cta{position:relative;height:auto;min-height:760px;}.final-cta__bg{transform:none!important;}}"
)

pat = re.compile(
    r"\.final-cta-scroller\{height:auto;background:none;\}.*?@media \(prefers-reduced-motion:reduce\)\{[^}]+\}\.final-cta__frame\{[^}]+\}\}",
    re.DOTALL,
)
# fallback: simpler anchor replace from .final-cta-scroller{height:auto
start = text.find(".final-cta-scroller{height:auto;background:none;}")
if start < 0:
    start = text.find(".final-cta-scroller{height:auto")
end = text.find(".final-cta h2{", start)
if start < 0 or end < 0:
    raise SystemExit(f"markers not found start={start} end={end}")

text = text[:start] + new_block + text[end:]
CSS.write_text(text, encoding="utf-8")
print("patched final-cta css")
