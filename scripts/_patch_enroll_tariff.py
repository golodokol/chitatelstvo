from pathlib import Path

p = Path(r"C:\Users\Оля\Documents\Читательство\docs\tilda-zero-main\chit-zero.js")
t = p.read_text(encoding="utf-8")
old = (
    'function k(){var e="";try{e=sessionStorage.getItem("chit_enroll_group")||""}catch(t){}'
    "if(e&&t[e]){try{sessionStorage.removeItem(\"chit_enroll_group\")}catch(t){}"
    'var a=document.querySelector(\'#course-catalog [data-group="\'+e+\'"]\');'
    "a&&s(a.getAttribute(\"data-course-title\")||t[e].label||\"\",a.getAttribute(\"data-course-meta\")||\"\",!0),d(e),b()}}"
)
new = (
    'function k(){var e="",r="";try{e=sessionStorage.getItem("chit_enroll_group")||""}catch(t){}'
    'try{r=sessionStorage.getItem("chit_enroll_tariff")||""}catch(n){}'
    "if(e&&t[e]){try{sessionStorage.removeItem(\"chit_enroll_group\")}catch(t){}"
    "try{sessionStorage.removeItem(\"chit_enroll_tariff\")}catch(o){}"
    'var a=document.querySelector(\'#course-catalog [data-group="\'+e+\'"]\');'
    "a&&s(a.getAttribute(\"data-course-title\")||t[e].label||\"\",a.getAttribute(\"data-course-meta\")||\"\",!0),d(e);"
    'if(r){var i=document.querySelector(\'#chit-tariffs [data-tariff="\'+r+\'"]\');i&&i.click()}b()}}'
)
if old not in t:
    raise SystemExit("old snippet not found")
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("ok", "chit_enroll_tariff" in p.read_text(encoding="utf-8"))
