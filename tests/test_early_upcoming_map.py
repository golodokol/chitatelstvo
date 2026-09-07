"""Тропа модуля: для всех «скоро», черновики 1–4 только в staff-кабинете."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from gamification import cabinet_ui
from lessons.staff_preview import (
    is_staff_preview_draft_lesson,
    is_staff_preview_token,
    staff_preview_lesson_slug,
)


class UpcomingTrailTests(unittest.TestCase):
    def test_upcoming_shows_soon_and_not_playable(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
        )
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["url"] is None for row in rows))
        self.assertTrue(all(row["unlocked"] is False for row in rows))
        self.assertTrue(all(row["overlay_label"] == "скоро" for row in rows))
        self.assertTrue(all(row["preview_open"] is False for row in rows))
        self.assertEqual(rows[0]["title"], "Мотор на поляне")

    def test_staff_preview_signs_lessons_1_to_4(self):
        with patch(
            "api.lesson_signing.build_lesson_url",
            lambda child_id, slug: f"/lesson/{slug}?child={child_id}&sig=x",
        ):
            rows = cabinet_ui._upcoming_module_lessons(
                group_code="early-letters",
                assets_base="https://example.test",
                staff_preview=True,
                child_id="11111111-1111-1111-1111-111111111111",
            )
        self.assertTrue(all(row["overlay_label"] == "скоро" for row in rows))
        self.assertTrue(rows[0]["url"])
        self.assertIn("lesson-01", rows[0]["url"])
        self.assertTrue(rows[3]["url"])
        self.assertIsNone(rows[4]["url"])

    def test_trial_track_exposes_purchase_cta_without_lesson_urls(self):
        with patch(
            "api.lesson_signing.build_lesson_url",
            lambda child_id, slug: f"/lesson/{slug}?child={child_id}&sig=x",
        ):
            cab = cabinet_ui.build_child_cabinet(
                name="Полина",
                level="Новичок",
                points=0,
                earned_badges=[],
                events=[],
                lesson_links=[],
                tracks=[
                    {
                        "group_code": "early-letters",
                        "group_label": "Буквы оживают",
                        "tariff_code": "trial",
                        "lesson_links": [],
                    }
                ],
                assets_base="https://example.test",
                child_id="11111111-1111-1111-1111-111111111111",
            )
        track = cab["tracks"][0]
        self.assertEqual(track["map_cta_label"], "Купить продолжение")
        self.assertIn("закрыты", track["map_cta_note"] or "")
        self.assertTrue(track["buy_url"])
        self.assertIsNone(track["upcoming_lessons"][0]["url"])
        self.assertEqual(track["upcoming_lessons"][0]["overlay_label"], "скоро")

    def test_staff_token_opens_draft_links_on_trial_map(self):
        with patch(
            "api.lesson_signing.build_lesson_url",
            lambda child_id, slug: f"/lesson/{slug}?child={child_id}&sig=x",
        ):
            cab = cabinet_ui.build_child_cabinet(
                name="Полина",
                level="Новичок",
                points=0,
                earned_badges=[],
                events=[],
                lesson_links=[],
                tracks=[
                    {
                        "group_code": "early-stories",
                        "group_label": "Первые истории",
                        "tariff_code": "trial",
                        "lesson_links": [],
                    }
                ],
                assets_base="https://example.test",
                child_id="11111111-1111-1111-1111-111111111111",
                progress_token="rPUXWKEkXj21YesZFgR3Zx9bX73GP3Dq-SSRauOZVPg",
            )
        track = cab["tracks"][0]
        self.assertIn("проверки", track["map_cta_note"] or "")
        self.assertIn("lesson-01", track["upcoming_lessons"][0]["url"] or "")
        self.assertEqual(
            staff_preview_lesson_slug("early-stories", 1),
            "early-stories-self_paced-stage-1-lesson-01",
        )


class StaffPreviewHelpersTests(unittest.TestCase):
    def test_token_and_draft_lesson(self):
        self.assertTrue(
            is_staff_preview_token("rPUXWKEkXj21YesZFgR3Zx9bX73GP3Dq-SSRauOZVPg")
        )
        self.assertFalse(is_staff_preview_token("other"))
        self.assertTrue(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "self_paced",
                    "lesson_number": 2,
                }
            )
        )
        self.assertFalse(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "trial",
                    "lesson_number": 1,
                }
            )
        )
        self.assertFalse(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "self_paced",
                    "lesson_number": 5,
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
