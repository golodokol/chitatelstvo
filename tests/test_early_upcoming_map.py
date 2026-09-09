"""Staff preview: уроки 1–4 открыты только в указанном кабинете."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("LESSON_SIGNING_SECRET", "test-staff-preview-secret")

from gamification import cabinet_ui
from lessons.staff_preview import (
    is_staff_preview_draft_lesson,
    is_staff_preview_token,
    staff_preview_lesson_slug,
)


class UpcomingStaffPreviewTests(unittest.TestCase):
    def test_upcoming_closed_for_everyone_by_default(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
        )
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["url"] is None for row in rows))
        self.assertTrue(all(row["unlocked"] is False for row in rows))
        self.assertEqual(rows[0]["title"], "Машина на поляне")
        self.assertIn("scene-map-sounds-where-01.png", rows[0]["cover_url"])
        self.assertIn("scene-map-sounds-where-08.png", rows[7]["cover_url"])
        self.assertEqual(
            cabinet_ui._early_letters_where_map_url(3),
            "/static/early/letters/scene-map-sounds-where-03.png?v=20260909b",
        )

    def test_program_map_uses_single_base_and_eight_pins(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        program_map = cabinet_ui._early_letters_program_map(rows)
        self.assertIsNotNone(program_map)
        assert program_map is not None
        self.assertIn("scene-map-sounds-final.png", program_map["image_url"])
        self.assertEqual(len(program_map["pins"]), 8)
        self.assertEqual(program_map["pins"][0]["n"], 1)
        self.assertEqual(program_map["pins"][0]["x"], 16.09)
        self.assertEqual(program_map["pins"][0]["y"], 56.81)
        self.assertEqual(program_map["pins"][0]["tip"], "right")
        self.assertEqual(program_map["pins"][0]["state"], "open")
        self.assertEqual(program_map["pins"][4]["state"], "soon")
        self.assertEqual(program_map["pins"][1]["x"], 20.7)
        self.assertEqual(program_map["pins"][1]["y"], 36.94)
        self.assertEqual(program_map["pins"][1]["tip"], "left")

    def test_upcoming_opens_first_four_for_staff_preview(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["unlocked"] for row in rows[:4]))
        self.assertTrue(all(row["url"] for row in rows[:4]))
        self.assertTrue(all(row["url"] is None for row in rows[4:]))
        self.assertTrue(all(row["unlocked"] is False for row in rows[4:]))
        self.assertIn("early-letters-self_paced-stage-1-lesson-01", rows[0]["url"])
        self.assertIn("early-letters-self_paced-stage-1-lesson-04", rows[3]["url"])

    def test_staff_preview_helpers(self):
        token = "rPUXWKEkXj21YesZFgR3Zx9bX73GP3Dq-SSRauOZVPg"
        self.assertTrue(is_staff_preview_token(token))
        self.assertFalse(is_staff_preview_token("other"))
        self.assertEqual(
            staff_preview_lesson_slug("early-stories", 2),
            "early-stories-self_paced-stage-1-lesson-02",
        )
        self.assertTrue(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "self_paced",
                    "lesson_number": 3,
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


if __name__ == "__main__":
    unittest.main()
