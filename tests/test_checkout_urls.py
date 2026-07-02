from services.checkout_urls import build_meeting_addon_pay_url


def test_meeting_addon_pay_url():
    url = build_meeting_addon_pay_url(
        module_id=19,
        chosen_stage="1",
        chosen_tale_number=1,
        lesson_slug="tsarevna-lyagushka",
        group_code="grade-1",
    )
    assert url.startswith("https://chitatelstvo.ru/oplata?")
    assert "tariff=meeting_addon" in url
    assert "module_id=19" in url
    assert "chosen_stage=1" in url
    assert "chosen_tale_number=1" in url
    assert "lesson_slug=tsarevna-lyagushka" in url
    assert "group=grade-1" in url
    assert "group_code=grade-1" in url
    assert url.endswith("#order:::uid=168614126213")
