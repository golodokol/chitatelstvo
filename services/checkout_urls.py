"""Checkout URLs for Tilda /oplata (cross-origin safe via query string)."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode

from config.settings import ROOT

SITE_URL = "https://chitatelstvo.ru"
_ORDER_CONFIG_PATH = ROOT / "docs" / "tilda-zero-main" / "order-config.json"


def _load_order_config() -> dict:
    try:
        return json.loads(_ORDER_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_oplata_checkout_url(
    *,
    tariff: str,
    module_id: int,
    chosen_stage: str,
    chosen_tale_number: int,
    lesson_slug: str = "",
    group_code: str = "",
    notification_channel: str = "email",
) -> str:
    """Build /oplata URL with checkout query params and #order hash for direct cart."""
    cfg = _load_order_config()
    products = cfg.get("products") or {}
    product = products.get(tariff) or {}
    uid = product.get("uid", "")

    params: dict[str, str | int] = {
        "tariff": tariff,
        "module_id": module_id,
        "chosen_stage": chosen_stage,
        "chosen_tale_number": chosen_tale_number,
        "notification_channel": notification_channel,
    }
    if lesson_slug:
        params["lesson_slug"] = lesson_slug
    if group_code:
        params["group"] = group_code
        params["group_code"] = group_code

    pay_base = cfg.get("pay_page_url") or f"{SITE_URL}/oplata"
    url = f"{pay_base}?{urlencode(params)}"
    if uid:
        url += f"#order:::uid={uid}"
    return url


def build_meeting_addon_pay_url(
    *,
    module_id: int,
    chosen_stage: str,
    chosen_tale_number: int,
    lesson_slug: str = "",
    group_code: str = "",
) -> str:
    return build_oplata_checkout_url(
        tariff="meeting_addon",
        module_id=module_id,
        chosen_stage=chosen_stage,
        chosen_tale_number=chosen_tale_number,
        lesson_slug=lesson_slug,
        group_code=group_code,
        notification_channel="email",
    )
