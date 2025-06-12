import unittest
from unittest.mock import mock_open, patch, MagicMock
from habits import load_habits_from_csv, is_today_in_days, HabitTrackerApp
import json

class TestHabits(unittest.TestCase):
    def test_load_habits_from_csv(self):
        csv_content = "Habits,SubItems,Days\nExercise,Pushups,Mon-Wed\nExercise,Situps,Tue-Thu\n"
        with patch("builtins.open", mock_open(read_data=csv_content)):
            habits = load_habits_from_csv("dummy.csv")
            self.assertIn("Exercise", habits)
            self.assertEqual(len(habits["Exercise"]), 2)
            self.assertEqual(habits["Exercise"][0]["name"], "Pushups")
            self.assertEqual(habits["Exercise"][0]["days"], ["Mon", "Wed"])

    def test_is_today_in_days(self):
        self.assertTrue(is_today_in_days([]))  # No days means always True
        self.assertIn(is_today_in_days(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]), [True, False])


if __name__ == "__main__":
    unittest.main()