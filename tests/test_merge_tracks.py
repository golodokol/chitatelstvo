from services.cabinet import merge_tracks_by_group, _dedupe_lesson_links


def test_merge_tracks_by_group_keeps_grade1_together():
    tracks = [
        {
            "group_code": "grade-1",
            "group_label": "1 класс",
            "module_title": "Разовое · Царевна",
            "module_id": 11,
            "tariff_code": "single",
            "lesson_links": [
                {
                    "slug": "grade-1-single-lesson-01",
                    "title": "Царевна лягушка",
                    "tale_slug": "grade-1-stage1-tale-01",
                    "url": "/a",
                    "week_in_stage": 1,
                    "module_week": 1,
                    "stage": "stage-1",
                }
            ],
            "has_meetings": False,
        },
        {
            "group_code": "extra-6-8",
            "group_label": "Внеклассное 6–8",
            "module_title": "Разовое · Кольцо",
            "module_id": 22,
            "tariff_code": "single",
            "lesson_links": [
                {
                    "slug": "extra-single",
                    "title": "Волшебное кольцо",
                    "tale_slug": "extra-tale-01",
                    "url": "/b",
                    "week_in_stage": 1,
                    "module_week": 1,
                    "stage": "stage-1",
                }
            ],
            "has_meetings": False,
        },
        {
            "group_code": "grade-1",
            "group_label": "1 класс",
            "module_title": "Разовое · Толстой",
            "module_id": 12,
            "tariff_code": "single",
            "lesson_links": [
                {
                    "slug": "grade-1-single-lesson-01",
                    "title": "Акула",
                    "tale_slug": "grade-1-stage1-tale-02",
                    "url": "/c",
                    "week_in_stage": 2,
                    "module_week": 2,
                    "stage": "stage-1",
                }
            ],
            "has_meetings": False,
        },
    ]

    merged = merge_tracks_by_group(tracks)
    assert len(merged) == 2
    assert merged[0]["group_code"] == "grade-1"
    titles = [les["title"] for les in merged[0]["lesson_links"]]
    assert titles == ["Царевна лягушка", "Акула"]
    assert merged[1]["group_code"] == "extra-6-8"


def test_dedupe_prefers_url():
    links = [
        {"title": "A", "tale_slug": "t1"},
        {"title": "A", "tale_slug": "t1", "url": "/open"},
    ]
    out = _dedupe_lesson_links(links)
    assert len(out) == 1
    assert out[0]["url"] == "/open"
