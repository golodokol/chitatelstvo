# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

d = Path(__file__).resolve().parents[1] / "docs" / "tilda-zero-main"
src = d / "chit-zero.src.js"
out = d / "chit-zero.js"
subprocess.check_call(
    f'npx --yes terser "{src}" -c -m -o "{out}"',
    shell=True,
)
print("zero", out.stat().st_size)
text = out.read_text(encoding="utf-8")
print("has intent flag", "__chitQuizUserIntent" in text)
