from unittest import TestCase, main

import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from utils.utils import (
    get_all_available_courses_for_allocation,
    get_all_elective_courses_with_professor_qualified,
    get_course_schedule,
    get_courses_by_time,
    get_courses_by_day,
    get_possible_schedules,
    get_qualified_courses_for_professor,
    remove_courses,
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

        result = get_course_schedule(mock_get_courses_set, "OBG-BCC1-2")
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

        result = get_courses_by_time(mock_courses, "08:00-10:00")
        expected_result = {"OBG-BCC1-1"}

        self.assertEqual(result, expected_result)

        result = get_courses_by_time(mock_courses, "15:00-17:00")
        expected_result = {"OBG-BCC1-2"}

        self.assertEqual(result, expected_result)

        result = get_courses_by_time(mock_courses, "13:00-15:00")
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

        result = get_courses_by_day(mock_courses, "SEG")
        expected_result = set(["OBG-BCC1-1"])

        self.assertEqual(result, expected_result)

        result = get_courses_by_day(mock_courses, "QUA")
        expected_result = set(["OBG-BCC1-1"])

        self.assertEqual(result, expected_result)

        result = get_courses_by_day(mock_courses, "TER")
        expected_result = set(["OBG-BCC1-2"])

        self.assertEqual(result, expected_result)

        result = get_courses_by_day(mock_courses, "QUI")
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


class TestGetQualifiedCoursesForProfessor(TestCase):
    def test_professor_with_qualified_courses(self):
        mock_courses_set = {
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
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        mock_professors_set = {
            "ProfA": {"qualified_courses": ["ICP131"]},
            "ProfB": {"qualified_courses": ["ICP123"]},
        }

        result = get_qualified_courses_for_professor(
            mock_courses_set, mock_professors_set, "ProfA"
        )
        expected_result = {"OBG-BCC1-1"}

        self.assertEqual(result, expected_result)

        result = get_qualified_courses_for_professor(
            mock_courses_set, mock_professors_set, "ProfB"
        )
        expected_result = {"OBG-BCC1-2"}

        self.assertEqual(result, expected_result)

    def test_professor_with_no_qualified_courses(self):
        mock_courses_set = {
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
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        mock_professors_set = {"ProfA": {"qualified_courses": ["ICP999"]}}

        result = get_qualified_courses_for_professor(
            mock_courses_set, mock_professors_set, "ProfA"
        )
        expected_result = set()

        self.assertEqual(result, expected_result)

    def test_dummy_professor(self):
        mock_courses_set = {
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
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        mock_professors_set = {}

        result = get_qualified_courses_for_professor(
            mock_courses_set, mock_professors_set, "DUMMY"
        )
        expected_result = {"OBG-BCC1-1", "OBG-BCC1-2"}

        self.assertEqual(result, expected_result)

    def test_raises_keyerror_if_professor_not_found(self):
        mock_courses_set = {
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
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        mock_professors_set = {"ProfA": {"qualified_courses": ["ICP131"]}}

        result = get_qualified_courses_for_professor(
            mock_courses_set, mock_professors_set, "ProfB"
        )
        expected_result = set()

        self.assertEqual(result, expected_result)
        self.assertRaises(KeyError)


class TestRemoveManualCourses(TestCase):
    def test_remove_manual_courses(self):
        mock_courses = {"OBG-BCC1-1", "OBG-BCC1-2"}
        mock_manual_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00",
                "course_type": "OBG",
            }
        }

        result = remove_courses(mock_courses, mock_manual_courses)
        expected_result = {"OBG-BCC1-2"}

        self.assertEqual(result, expected_result)

    def test_remove_manual_courses_with_no_manual_courses(self):
        mock_courses = {"OBG-BCC1-1", "OBG-BCC1-2"}
        mock_manual_courses = {}

        result = remove_courses(mock_courses, mock_manual_courses)
        expected_result = mock_courses

        self.assertEqual(result, expected_result)

    def test_remove_manual_courses_with_all_manual_courses(self):
        mock_courses = {"OBG-BCC1-1", "OBG-BCC1-2"}
        mock_manual_courses = {
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
                "day": "TER,QUI",
                "time": "15:00-17:00",
                "course_type": "SVC",
            },
        }

        result = remove_courses(mock_courses, mock_manual_courses)
        expected_result = set()

        self.assertEqual(result, expected_result)

    def test_remove_manual_courses_with_non_existent_manual_courses(self):
        mock_courses = {"OBG-BCC1-1", "OBG-BCC1-2"}
        mock_manual_courses = dict()

        result = remove_courses(mock_courses, mock_manual_courses)
        expected_result = mock_courses

        self.assertEqual(result, expected_result)


class TestGetAllElectiveCoursesWithProfessorQualified(TestCase):
    def test_elective_courses_with_qualified_professors(self):
        mock_courses = {
            "OPT-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "course_type": "OPT",
            }
        }

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP131"]},
            "ProfB": {"qualified_courses": ["ICP123"]},
        }

        result = get_all_elective_courses_with_professor_qualified(mock_courses, mock_professors)
        expected_result = {"OPT-BCC1-1", "OPT-BCC1-2"}

        self.assertEqual(result, expected_result)

    def test_no_elective_courses_with_qualified_professors(self):
        mock_courses = {
            "OPT-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "course_type": "OPT",
            },
        }

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP999"]},
            "ProfB": {"qualified_courses": ["ICP888"]},
        }

        result = get_all_elective_courses_with_professor_qualified(mock_courses, mock_professors)
        expected_result = set()

        self.assertEqual(result, expected_result)

    def test_mixed_elective_courses_with_qualified_professors(self):
        mock_courses = {
            "OPT-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "course_type": "OPT",
            },
        }

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP131"]},
            "ProfB": {"qualified_courses": ["ICP999"]},
        }

        result = get_all_elective_courses_with_professor_qualified(mock_courses, mock_professors)
        expected_result = {"OPT-BCC1-1"}

        self.assertEqual(result, expected_result)


class TestGetAllAvailableCoursesForAllocation(TestCase):
    def test_all_available_courses_for_allocation(self):
        mock_required_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00",
                "course_type": "OBG",
            }
        }

        mock_elective_courses = {
            "OPT-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-3": {
                "course_id": "ICPXXX",
                "credits": 4,
                "course_type": "OPT",
            },
        }

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP131"]},
            "ProfB": {"qualified_courses": ["ICP123"]},
        }

        result = get_all_available_courses_for_allocation(mock_required_courses, mock_elective_courses, mock_professors)
        
        mock_elective_courses["OPT-BCC1-1"].update({"day": "NÃO DEFINIDO", "time": "NÃO DEFINIDO"})
        mock_elective_courses["OPT-BCC1-2"].update({"day": "NÃO DEFINIDO", "time": "NÃO DEFINIDO"})

        expected_result = {
            "OPT-BCC1-1": mock_elective_courses["OPT-BCC1-1"],
            "OPT-BCC1-2": mock_elective_courses["OPT-BCC1-2"],
            "OBG-BCC1-1": mock_required_courses["OBG-BCC1-1"],
        }

        self.assertEqual(result, expected_result)

    def test_no_available_elective_courses_for_allocation(self):
        mock_required_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00",
                "course_type": "OBG",
            }
        }

        mock_elective_courses = {
            "OPT-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "course_type": "OPT",
            },
            "OPT-BCC1-2": {
                "course_id": "ICP123",
                "credits": 4,
                "course_type": "OPT",
            },
        }

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP999"]},
            "ProfB": {"qualified_courses": ["ICP888"]},
        }

        result = get_all_available_courses_for_allocation(mock_required_courses, mock_elective_courses, mock_professors)
        expected_result = mock_required_courses

        self.assertEqual(result, expected_result)

    def test_only_required_courses_for_allocation(self):
        mock_required_courses = {
            "OBG-BCC1-1": {
                "course_id": "ICP131",
                "credits": 4,
                "day": "SEG,QUA",
                "time": "13:00-15:00",
                "course_type": "OBG",
            }
        }

        mock_elective_courses = {}

        mock_professors = {
            "ProfA": {"qualified_courses": ["ICP131"]},
            "ProfB": {"qualified_courses": ["ICP123"]},
        }

        result = get_all_available_courses_for_allocation(mock_required_courses, mock_elective_courses, mock_professors)
        expected_result = mock_required_courses

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
