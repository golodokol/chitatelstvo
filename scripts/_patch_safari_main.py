#!/usr/bin/env python3
"""Bump main-page asset version and Safari-safe quiz loader."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VERSION = "20260823s"

NEW_LOADER = (
    '<script id="chit-quiz-loader">(function(){var A="https://api.chitatelstvo.ru/assets/",'
    f'V="{VERSION}",busy=0,done=0,q=[];'
    "function run(){while(q.length)(q.shift())();}"
    "function rememberTrial(el){if(!el||!el.getAttribute)return;var slug=el.getAttribute(\"data-trial-slug\");"
    "if(!slug)return;try{var age=el.getAttribute(\"data-trial-age\")||\"\";"
    "sessionStorage.setItem(\"chit_trial\",JSON.stringify({age:age,slug:slug,"
    "title:el.getAttribute(\"data-trial-title\")||\"\"}));"
    "var hint=age===\"4-6\"?\"5\":(age===\"5-7\"?\"6\":(age===\"6-8\"?\"7\":(age===\"9-11\"?\"10\":\"\")));"
    "if(hint)sessionStorage.setItem(\"chit_trial_age_hint\",hint);}catch(err){}}"
    "function openReady(){if(window.chitQuizOpen)window.chitQuizOpen();}"
    "function appendJs(){if(document.querySelector('script[src*=\"chit-quiz.js\"]'))return;"
    "var s=document.createElement(\"script\");s.src=A+\"chit-quiz.js?v=\"+V;"
    "s.onload=function(){done=1;busy=0;run();openReady();};s.onerror=function(){busy=0;};"
    "document.head.appendChild(s);}"
    "window.chitLoadQuiz=function(cb){if(done){if(cb)cb();return openReady();}if(cb)q.push(cb);"
    "if(busy)return;busy=1;"
    "if(!document.querySelector('link[href*=\"chit-quiz.css\"]')){"
    "var c=document.createElement(\"link\");c.rel=\"stylesheet\";c.href=A+\"chit-quiz.css?v=\"+V;"
    "document.head.appendChild(c);}appendJs();setTimeout(function(){if(!done)appendJs();},2000);};"
    "document.addEventListener(\"click\",function(e){if(done)return;"
    "var t=e.target.closest('[href=\"#quiz\"],[data-qz-open]');if(!t)return;"
    "e.preventDefault();e.stopImmediatePropagation();rememberTrial(t);window.chitLoadQuiz();},true);"
    "if(location.hash===\"#quiz\")window.chitLoadQuiz();})();</script>"
)

SAFARI_CSS_FIX = (
    '<script id="chit-css-safari-fix">(function(){var l=document.getElementById("chit-zero-css");'
    'if(l){l.media="all";}})();</script>'
)


def main() -> None:
    bp = ROOT / "scripts" / "build_tilda_upload.py"
    bp_text = bp.read_text(encoding="utf-8")
    bp_text = re.sub(r'VERSION = "[^"]+"', f'VERSION = "{VERSION}"', bp_text, count=1)
    bp_text = bp_text.replace(
        "padding-bottom:calc(54px + env(safe-area-inset-bottom))",
        "padding-bottom:calc(72px + env(safe-area-inset-bottom))",
    )
    bp.write_text(bp_text, encoding="utf-8")

    for name in ("00-tilda-zero-upload.html", "00-tilda-lite.html"):
        path = DIR / name
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"20260822k", VERSION, text)
        text = re.sub(
            r'<script id="chit-quiz-loader">[\s\S]*?</script>',
            NEW_LOADER,
            text,
            count=1,
        )
        if "chit-css-safari-fix" not in text:
            text = text.replace(
                f'<link id="chit-zero-css" rel="stylesheet" href="https://api.chitatelstvo.ru/assets/chit-zero.css?v={VERSION}" media="print" onload="this.media=\'all\'">',
                f'<link id="chit-zero-css" rel="stylesheet" href="https://api.chitatelstvo.ru/assets/chit-zero.css?v={VERSION}" media="print" onload="this.media=\'all\'">'
                + SAFARI_CSS_FIX,
                1,
            )
        path.write_text(text, encoding="utf-8")
        print(name, "patched", VERSION in path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
