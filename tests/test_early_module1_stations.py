"""Станции уроков 1–4 модуля: сетки лабиринта проходимы."""

from __future__ import annotations

import unittest

from lessons.early_module1_lessons import LETTERS, STORIES, stations_for


def _maze_ok(station: dict) -> bool:
    grid = station["grid"]
    letter = station["letter"]
    sr, sc = station["start"]
    er, ec = station["end"]
    if grid[sr][sc] != letter or grid[er][ec] != letter:
        return False
    rows, cols = len(grid), len(grid[0])
    seen = {(sr, sc)}
    stack = [(sr, sc)]
    while stack:
        r, c = stack.pop()
        if (r, c) == (er, ec):
            return True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen:
                if grid[nr][nc] == letter:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
    return False


class Module1StationsTests(unittest.TestCase):
    def test_all_four_lessons_have_stations(self):
        for n in (1, 2, 3, 4):
            letters = stations_for("letters", n)
            stories = stations_for("stories", n)
            self.assertGreaterEqual(len(letters), 8)
            self.assertGreaterEqual(len(stories), 7)
            self.assertEqual(letters[-1]["kind"], "reward")
            self.assertEqual(letters[0]["id"], "trail")
            expected_scene = {
                1: "/static/early/letters/scene-m-meadow-intro.jpg",
                2: "/static/early/letters/scene-u-echo-intro.jpg",
                3: "/static/early/letters/scene-o-pond-intro.jpg",
                4: "/static/early/letters/scene-map-sounds-where-04.png",
            }[n]
            self.assertEqual(letters[0]["scene_image"], expected_scene)
            self.assertEqual(stories[-1]["kind"], "reward")

    def test_letter_mazes_have_path(self):
        for n, stations in LETTERS.items():
            for st in stations:
                if st.get("kind") == "letter_maze":
                    self.assertTrue(_maze_ok(st), f"lesson {n} {st['id']}")

    def test_three_sparks_on_letter_lessons(self):
        for n, stations in LETTERS.items():
            sparks = [s for s in stations if s.get("spark")]
            self.assertGreaterEqual(len(sparks), 3, n)


if __name__ == "__main__":
    unittest.main()
