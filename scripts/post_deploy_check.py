#!/usr/bin/env python3
"""Быстрая проверка после деплоя (без email). Exit 1 при сбое."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_monitor():
    path = ROOT / "scripts" / "monitor_health.py"
    spec = importlib.util.spec_from_file_location("monitor_health", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    monitor = _load_monitor()
    cfg = monitor.load_env_file(ROOT / ".env")
    results = monitor.run_checks(cfg)
    failed = [item for item in results if not item.ok]
    for item in results:
        mark = "OK" if item.ok else "FAIL"
        print(f"[{mark}] {item.name}: {item.detail}")
    if failed:
        print(f"POST_DEPLOY_FAIL ({len(failed)} checks)")
        return 1
    print("POST_DEPLOY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
