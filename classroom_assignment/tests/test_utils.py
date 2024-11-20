from unittest import TestCase, main

import sys
import os
from unittest.mock import patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from utils.utils import (
    get_section_schedule,
    get_section_by_time,
    get_section_by_day,
    get_possible_schedules,
    treat_and_save_results,
)


class TestUtils(TestCase):
    def test_get_schedule_from_course(self):
        mock_get_courses_set = {
            "OBG-BCC1-1": {
                "course_id": "ICP131,ICP222",
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
                "course_type": "SVC",
            },
        }

        result = get_section_schedule(mock_get_courses_set, "OBG-BCC1-2")
        expected_result = ("TER,QUI", "15:00-17:00")

        self.assertEqual(result, expected_result)

    def test_get_courses_by_time(self):
        mock_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131,ICP222",
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
                "course_type": "SVC",
            },
        }

        result = get_section_by_time(mock_courses, "08:00-10:00")
        expected_result = {"OBG-BCC1-1"}

        self.assertEqual(result, expected_result)

        result = get_section_by_time(mock_courses, "15:00-17:00")
        expected_result = {"OBG-BCC1-2"}

        self.assertEqual(result, expected_result)

        result = get_section_by_time(mock_courses, "13:00-15:00")
        expected_result = {"OBG-BCC1-1"}

        self.assertEqual(result, expected_result)

    def test_get_courses_by_day(self):
        mock_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131,ICP222",
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
                "course_type": "SVC",
            },
        }

        result = get_section_by_day(mock_courses, "SEG")
        expected_result = set(["OBG-BCC1-1"])

        self.assertEqual(result, expected_result)

        result = get_section_by_day(mock_courses, "QUA")
        expected_result = set(["OBG-BCC1-1"])

        self.assertEqual(result, expected_result)

        result = get_section_by_day(mock_courses, "TER")
        expected_result = set(["OBG-BCC1-2"])

        self.assertEqual(result, expected_result)

        result = get_section_by_day(mock_courses, "QUI")
        expected_result = set(["OBG-BCC1-2"])

        self.assertEqual(result, expected_result)


class TestGetPossibleSchedules(TestCase):
    def test_get_possible_schedules(self):
        mock_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131,ICP222",
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
                "course_type": "SVC",
            },
        }

        result = get_possible_schedules(mock_courses)
        expected_days = ["SEG,QUA", "TER,QUI"]
        expected_times = ["13:00-15:00,08:00-10:00", "15:00-17:00"]

        self.assertEqual(set(result[0]), set(expected_days))
        self.assertEqual(set(result[1]), set(expected_times))

    def test_get_schedule_without_schedules(self):

        mock_courses = {}
        result = get_possible_schedules(mock_courses)
        expected_days = []
        expected_times = []

        self.assertEqual(result[0], expected_days)
        self.assertEqual(result[1], expected_times)

    def test_get_courses_with_same_schedule(self):

        mock_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00",
                "course_type": "OBG",
            },
            "OBG-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "day": "SEG,QUI",
                "time": "13:00-15:00",
                "course_type": "SVC",
            },
        }

        result = get_possible_schedules(mock_courses)
        expected_days = list(set(["SEG,QUA", "SEG,QUI"]))
        expected_times = list(set(["13:00-15:00"]))

        self.assertEqual(result[0], expected_days)
        self.assertEqual(result[1], expected_times)

# class TestTreatAndSaveResults(TestCase):

#     @patch("utils.utils.save_results_to_csv")
#     def test_treat_and_save_results(self, mock_save_results_to_csv):

#         # E2011 (LAB 1)_OBG-BCC2-7_SEG,QUA_10:00-12:00/1.0
#         # F2007_OBG-BCC2-5_TER,QUI_13:00-15:00/1.0
#         # CapDiff_A201_OBG-BCC2-7/70.0
#         # CapDiff_A201_OBG-BCC2-5/70.0
#         # CapDiff_A202_OBG-BCC2-7/70.0

#         timeschedule_mock = [
#            "E2011 (LAB 1)_OBG-BCC2-7_SEG,QUA_10:00-12:00/1.0",
#            "F2007_OBG-BCC2-5_TER,QUI_13:00-15:00/1.0"
#         ]

#         sections_mock = {
#             "OBG-BCC1-1": {
#                 "course_id": "ICP131",
#                 "course_name": "Programação de Computadores I",
#                 "credits": 4,
#                 "course_type": "OBG",
#                 "class_type": "Gradução",
#                 "capacity": 40,
#                 "responsable_institute": "IC",
#                 "classroom_type": "Sala",
#                 "term": 1
#             },
#             "OBG-BCC1-2": {
#                 "course_id": "ICP132",
#                 "course_name": "Processo de Software",
#                 "credits": 4,
#                 "course_type": "OBG",
#                 "class_type": "Gradução",
#                 "capacity": 30,
#                 "responsable_institute": "IC",
#                 "classroom_type": "Sala",
#                 "term": 1
#             },
#         }

#         result = treat_and_save_results(timeschedule_mock, sections_mock)

#         timeschedule = [
#             [
#                 "IC",
#                 "Adriana Vivacqua",
#                 "ICP131",
#                 "Programação de Computadores I",
#                 "SEG,QUA",
#                 "13:00-15:00,08:00-10:00",
#                 40,
#                 "Sala",
#                 "OBG",
#                 1
#             ],
#             [
#                 "IC",
#                 "Daniel Sadoc",
#                 "ICP132",
#                 "Processo de Software",
#                 "TER,QUI",
#                 "15:00-17:00",
#                 30,
#                 "Sala",
#                 "OBG",
#                 1
#             ],
#         ]

#         expected_result = timeschedule

#         mock_save_results_to_csv.assert_called()
#         self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
