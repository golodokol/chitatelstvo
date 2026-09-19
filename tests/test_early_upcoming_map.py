"""Staff preview: early-уроки открыты только в указанном кабинете."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("LESSON_SIGNING_SECRET", "test-staff-preview-secret")

from gamification import cabinet_ui
from lessons.staff_preview import (
    is_staff_preview_draft_lesson,
    is_staff_preview_token,
    list_staff_preview_catalog,
    staff_preview_lesson_slug,
)


class UpcomingStaffPreviewTests(unittest.TestCase):
    def test_upcoming_closed_for_everyone_by_default(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
        )
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(row["url"] is None for row in rows[:8]))
        self.assertTrue(all(row["unlocked"] is False for row in rows[:8]))
        self.assertEqual(rows[0]["title"], "Машина на поляне")
        self.assertIn("scene-map-sounds-where-01.png", rows[0]["cover_url"])
        self.assertIn("scene-map-sounds-where-08.png", rows[7]["cover_url"])
        self.assertEqual(
            cabinet_ui._early_letters_where_map_url(3),
            f"/static/early/letters/scene-map-sounds-where-03.png?v={cabinet_ui.EARLY_ASSETS_VERSION}",
        )

    def test_program_map_uses_single_base_and_eight_pins(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        stage1 = [r for r in rows if str(r.get("stage") or "stage-1") == "stage-1"][:8]
        program_map = cabinet_ui._early_letters_program_map(stage1)
        self.assertIsNotNone(program_map)
        assert program_map is not None
        self.assertIn("scene-map-sounds-final.png", program_map["image_url"])
        self.assertEqual(len(program_map["pins"]), 8)
        self.assertEqual(program_map["pins"][0]["n"], 1)
        self.assertEqual(program_map["pins"][0]["x"], 16.09)
        self.assertEqual(program_map["pins"][0]["y"], 56.81)
        self.assertEqual(program_map["pins"][0]["tip"], "right")
        self.assertEqual(program_map["pins"][0]["state"], "open")
        self.assertEqual(program_map["pins"][0]["label"], "пройти")
        self.assertEqual(program_map["pins"][4]["state"], "open")
        self.assertEqual(program_map["pins"][7]["state"], "open")
        self.assertTrue(all(p["state"] != "done" for p in program_map["pins"]))
        self.assertEqual(program_map["pins"][1]["x"], 20.7)
        self.assertEqual(program_map["pins"][1]["y"], 36.94)
        self.assertEqual(program_map["pins"][1]["tip"], "above")
        self.assertEqual(program_map["pins"][7]["tip"], "above")

    def test_stories_program_map_uses_home_map_and_open_labels(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-stories",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        stage1 = [r for r in rows if str(r.get("stage") or "stage-1") == "stage-1"][:8]
        self.assertEqual(len(stage1), 8)
        program_map = cabinet_ui._early_program_map("early-stories", stage1)
        self.assertIsNotNone(program_map)
        assert program_map is not None
        self.assertIn("scene-map-stories-final.jpg", program_map["image_url"])
        self.assertEqual(len(program_map["pins"]), 8)
        self.assertEqual(program_map["pins"][0]["x"], 16.0)
        self.assertEqual(program_map["pins"][0]["y"], 33.8)
        self.assertEqual(program_map["pins"][0]["label"], "пройти")
        self.assertEqual(program_map["pins"][0]["state"], "open")
        self.assertTrue(all(p["state"] == "open" for p in program_map["pins"]))
        self.assertEqual(program_map["pins"][3]["tip"], "left")
        # 5 мокрый кот → ванная; 6 плед → спальня; 7 Словик → крыльцо; 8 дом → библиотека
        self.assertEqual(program_map["pins"][4]["x"], 15.1)
        self.assertEqual(program_map["pins"][4]["y"], 68.8)
        self.assertEqual(program_map["pins"][5]["x"], 37.6)
        self.assertEqual(program_map["pins"][6]["x"], 63.3)
        self.assertEqual(program_map["pins"][7]["x"], 85.7)

    def test_stories_track_hides_lesson_cards_under_map(self):
        track = {
            "group_code": "early-stories",
            "group_label": "Первые истории",
            "tariff_code": "trial",
            "module_id": 23,
            "module_title": "Модуль 1",
            "lesson_links": [
                {
                    "slug": f"early-stories-self_paced-stage-1-lesson-{i:02d}",
                    "title": f"Урок {i}",
                    "group_code": "early-stories",
                    "tariff_code": "trial",
                    "url": f"/lesson/{i}",
                    "week_in_stage": i,
                    "stage": "stage-1",
                }
                for i in range(1, 9)
            ],
        }
        cab = cabinet_ui._build_track_section(
            track=track,
            events=[],
            claims=[],
            points=0,
            assets_base="https://example.test",
            cabinet_mode="trial_early",
            staff_preview=False,
            child_id=None,
        )
        self.assertIsNotNone(cab.get("program_map"))
        self.assertEqual(len(cab["program_map"]["pins"]), 8)
        self.assertEqual(cab.get("upcoming_lessons") or [], [])

    def test_program_map_marks_completed_pins_as_done(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        stage1 = [r for r in rows if str(r.get("stage") or "stage-1") == "stage-1"][:8]
        done = {cabinet_ui.canonical_tale_slug(stage1[0]["slug"])}
        program_map = cabinet_ui._early_letters_program_map(stage1, completed_slugs=done)
        assert program_map is not None
        self.assertEqual(program_map["pins"][0]["state"], "done")
        self.assertEqual(program_map["pins"][0]["label"], "пройден")
        self.assertEqual(program_map["pins"][1]["state"], "open")
        self.assertEqual(program_map["pins"][1]["label"], "пройти")

    def test_track_section_keeps_map_pins_without_module1_cards(self):
        track = {
            "group_code": "early-letters",
            "group_label": "Буквы оживают",
            "tariff_code": "trial",
            "module_id": 20,
            "module_title": "Модуль 1",
            "lesson_links": [
                {
                    "slug": f"early-letters-self_paced-stage-1-lesson-{i:02d}",
                    "title": f"Урок {i}",
                    "group_code": "early-letters",
                    "tariff_code": "trial",
                    "url": f"/lesson/{i}",
                    "week_in_stage": i,
                    "stage": "stage-1",
                }
                for i in range(1, 9)
            ],
        }
        cab = cabinet_ui._build_track_section(
            track=track,
            events=[],
            claims=[],
            points=0,
            assets_base="https://example.test",
            cabinet_mode="trial_early",
            staff_preview=False,
            child_id=None,
        )
        self.assertIsNotNone(cab.get("program_map"))
        self.assertEqual(len(cab["program_map"]["pins"]), 8)
        upcoming = cab.get("upcoming_lessons") or []
        self.assertEqual(len(upcoming), 3)
        self.assertTrue(all(str(r.get("stage")) != "stage-1" for r in upcoming))
        self.assertTrue(all(r.get("inactive") for r in upcoming))

    def test_upcoming_teaser_includes_locked_modules_2_to_4(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
        )
        self.assertEqual(len(rows), 11)
        locked = [r for r in rows if r.get("inactive")]
        self.assertEqual(len(locked), 3)
        self.assertEqual(
            [r["stage"] for r in locked],
            ["stage-2", "stage-3", "stage-4"],
        )
        self.assertTrue(all(r["overlay_label"] == "скоро" for r in locked))
        self.assertTrue(all(r["url"] is None for r in locked))
        self.assertTrue(all(r["unlocked"] is False for r in locked))
        self.assertTrue(
            all((r["buy_url"] or "").endswith("#programs") for r in locked)
        )
        self.assertTrue(
            all("module-soon-path.jpg" in (r["cover_url"] or "") for r in locked)
        )

    def test_upcoming_opens_module1_and_locks_later_modules_for_staff(self):
        rows = cabinet_ui._upcoming_module_lessons(
            group_code="early-letters",
            assets_base="https://example.test",
            staff_preview=True,
            child_id="11111111-1111-1111-1111-111111111111",
        )
        stage1 = [r for r in rows if str(r.get("stage") or "stage-1") == "stage-1"]
        locked = [r for r in rows if r.get("inactive")]
        self.assertEqual(len(stage1), 8)
        self.assertTrue(all(row["unlocked"] for row in stage1))
        self.assertTrue(all(row["url"] for row in stage1))
        self.assertIn("early-letters-self_paced-stage-1-lesson-01", stage1[0]["url"])
        self.assertEqual(len(locked), 3)
        self.assertEqual(locked[0]["title"], "Шипящая тропа")
        self.assertEqual(locked[2]["stage"], "stage-4")
        self.assertTrue(all(r["overlay_label"] == "скоро" for r in locked))
        self.assertTrue(
            all("module-soon-path.jpg" in (r["cover_url"] or "") for r in locked)
        )

    def test_staff_preview_helpers(self):
        token = "rPUXWKEkXj21YesZFgR3Zx9bX73GP3Dq-SSRauOZVPg"
        self.assertTrue(is_staff_preview_token(token))
        self.assertFalse(is_staff_preview_token("other"))
        self.assertEqual(
            staff_preview_lesson_slug("early-stories", 2),
            "early-stories-self_paced-stage-1-lesson-02",
        )
        self.assertEqual(
            staff_preview_lesson_slug("early-letters", 3, stage="stage-2"),
            "early-letters-self_paced-stage-2-lesson-03",
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
        self.assertTrue(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "self_paced",
                    "lesson_number": 8,
                    "stage": "stage-1",
                }
            )
        )
        self.assertTrue(
            is_staff_preview_draft_lesson(
                {
                    "group_code": "early-letters",
                    "tariff_code": "self_paced",
                    "lesson_number": 10,
                    "stage": "stage-2",
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
