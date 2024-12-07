import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import ClassroomAssignment


class TestInitializeVariablesAndCoefficients(unittest.TestCase):

    @patch("utils.utils.get_section_schedule")
    def setUp(self, mock_get_schedule) -> None:
        patch("utils.utils.save_results_to_csv").start()

        classrooms = {
            "Room1": {"capacity": 30, "classroom_type": "Sala"},
            "Room2": {"capacity": 20, "classroom_type": "Laboratório"},
        }
        sections = {
            "Section1": {"capacity": 25, "day": "SEG,QUA", "time": "10:00-12:00"},
            "Section2": {"capacity": 15, "day": "TER,QUI", "time": "08:00-10:00"},
        }
        mock_get_schedule.side_effect = lambda sections, section: (
            ("SEG,QUA", "10:00-12:00") if section == "Section1" else ("TER,QUI", "08:00-10:00")
        )

        self.timetabling = ClassroomAssignment(classrooms, sections)
        self.timetabling.initialize_variables_and_coefficients()
        return super().setUp()

    @unittest.skip("Not implemented yet")
    def test_set_coefficient_if_section_is_scheduled(self):
        pass

    @unittest.skip("Not implemented yet")
    def test_set_coefficient_to_zero_if_section_is_not_scheduled(self):
        pass


class TestAddCapacitySlackVariables(unittest.TestCase):

    def setUp(self) -> None:
        self.classrooms = {
            "Room1": {"capacity": 30, "classroom_type": "Sala"},
            "Room2": {"capacity": 20, "classroom_type": "Laboratório"},
        }
        self.sections = {
            "Section1": {"capacity": 25, "day": "SEG,QUA", "time": "10:00-12:00", "classroom_type": "Sala"},
            "Section2": {"capacity": 15, "day": "TER,QUI", "time": "08:00-10:00", "classroom_type": "Laboratório"},
        }
        self.timetabling = ClassroomAssignment(self.classrooms, self.sections)
        self.timetabling.add_capacity_slack_variables()
        return super().setUp()

    def test_add_capacity_slack_variables_for_all_classrooms(self):
        for classroom in self.classrooms.keys():
            self.assertIn(classroom, self.timetabling.slack_variables)


if __name__ == "__main__":
    unittest.main()
