import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import ClassroomAssignment


class TestInitializeVariablesAndCoefficients(unittest.TestCase):

    @patch("utils.utils.get_course_schedule")
    def setUp(self, mock_get_schedule) -> None:
        professor_permanent = {
            "Prof1": {
                "qualified_courses": ["ICP131"],
                "expertise": ["ED", "ES", "H"],
                "category": "PP",
            },
        }
        professor_substitute = {
            "Prof2": {
                "qualified_courses": [],
                "expertise": ["ED", "CD"],
                "category": "PS",
            },
        }
        professor_dummy = {
            "DUMMY": {
                "qualified_courses": ["*"],
                "expertise": ["*"],
                "category": "DUMMY",
            },
        }
        self.PROFESSORS = professor_permanent | professor_substitute | professor_dummy
        self.COURSES = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00,08:00-10:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "OBG",
            },
        }
        mock_get_schedule.side_effect = lambda courses, course: (
            ("SEG", "13:00-15:00") if course == "OBG-BCC1-1" else ("TER", "15:00-17:00")
        )

        self.timetabling = ClassroomAssignment(
            self.PROFESSORS,
            professor_permanent,
            professor_substitute,
            self.COURSES,
            {},
        )
        self.timetabling.initialize_variables_and_coefficients()
        return super().setUp()

    def test_set_coefficient_if_professor_is_qualified_for_class(self):

        expected_coefficient = 100

        self.assertIn("Prof1", self.timetabling.coefficients)
        self.assertIn("OBG-BCC1-1", self.timetabling.coefficients["Prof1"])

        for day, value in self.timetabling.coefficients["Prof1"]["OBG-BCC1-1"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.coefficients["Prof1"]["OBG-BCC1-1"][day][time],
                expected_coefficient,
            )

        self.assertIn("OBG-BCC1-1", self.timetabling.variables["Prof1"])

    def test_set_coefficient_to_zero_if_professor_is_not_qualified_for_class(self):

        self.assertIn("Prof1", self.timetabling.coefficients)
        self.assertIn("OBG-BCC1-2", self.timetabling.coefficients["Prof1"])

        for day, value in self.timetabling.coefficients["Prof1"]["OBG-BCC1-2"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.coefficients["Prof1"]["OBG-BCC1-2"][day][time], 0
            )

        self.assertIn("OBG-BCC1-2", self.timetabling.variables["Prof1"])

    def test_set_coefficient_specific_if_professor_is_dummy(self):

        self.assertIn("DUMMY", self.timetabling.coefficients)
        self.assertIn("OBG-BCC1-1", self.timetabling.coefficients["DUMMY"])
        self.assertIn("OBG-BCC1-2", self.timetabling.coefficients["DUMMY"])

        for day, value in self.timetabling.coefficients["DUMMY"]["OBG-BCC1-1"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.coefficients["DUMMY"]["OBG-BCC1-1"][day][time], 0.0001
            )

        for day, value in self.timetabling.coefficients["DUMMY"]["OBG-BCC1-2"].items():
            time = list(value.keys())[0]
            self.assertEqual(
                self.timetabling.coefficients["DUMMY"]["OBG-BCC1-2"][day][time], 0.0001
            )

        self.assertIn("OBG-BCC1-1", self.timetabling.variables["DUMMY"])
        self.assertIn("OBG-BCC1-2", self.timetabling.variables["DUMMY"])


class TestAddCreditSlackVariables(unittest.TestCase):

    def setUp(self) -> None:
        self.timetabling = ClassroomAssignment(
            ["Prof1", "Prof2"], ["Prof1"], ["Prof2"], {}, {}
        )
        self.timetabling.add_credit_slack_variables()
        return super().setUp()

    def test_add_credit_slack_variables(self):
        self.assertIn("Prof1", self.timetabling.slack_variables)

    def test_add_credit_slack_variables_only_for_permanent_professors(self):
        self.assertIn("Prof1", self.timetabling.slack_variables)
        self.assertNotIn("Prof2", self.timetabling.slack_variables)


if __name__ == "__main__":
    unittest.main()
