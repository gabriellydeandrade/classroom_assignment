from unittest import TestCase, main
from unittest.mock import patch
import sys
import os
import pandas as pd

from functools import wraps

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma


def mock_decorator(*args, **kwargs):
    """Decorate by doing nothing."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    return decorator


patch("cache_pandas.cache_to_csv", mock_decorator).start()

from database.service_google_sheet import (
    get_secion_allocation,
)
from database.transform_data import transform_sections_to_dict


class TestSectionAllocationFromGoogleSheets(TestCase):

    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_secion_allocation(self, mock_read_google_sheet):
        mock_data = pd.DataFrame(
            {
                "Instituto responsável": ["IC", "IC"],
                "Nome curto professor": ["Prof1", "Prof2"],
                "Código disciplina": ["Course1", "Course2"],
                "Nome disciplina": ["CourseName1", "CourseName2"],
                "Dia da semana": ["SEG,QUA", "TER"],
                "Horário": ["08:00-10:00", "10:00-12:00"],
                "Vagas": [30, 30],
                "Tipo sala": ["Laboratório", "Sala"],
                "Período": [1, 1],
            },
        )

        mock_read_google_sheet.return_value = mock_data

        result = get_secion_allocation()

        expected_data = pd.DataFrame(
            {
                "responsable_institute": ["IC", "IC"],
                "professor": ["Prof1", "Prof2"],
                "course_id": ["Course1", "Course2"],
                "course_name": ["CourseName1", "CourseName2"],
                "day": ["SEG,QUA", "TER"],
                "time": ["08:00-10:00", "10:00-12:00"],
                "capacity": [30, 30],
                "classroom_type": ["Laboratório", "Sala"],
                "term": [1, 1],
            }
        )

        mock_read_google_sheet.assert_called_once()
        pd.testing.assert_frame_equal(result, expected_data)


class TestTransformSectionAllocation(TestCase):

    def test_treat_section_allocation_with_correct_params(self):
        section_allocation = pd.DataFrame(
            {
                "institute": ["IC", "IC"],
                "professor": ["Prof1", "Prof2"],
                "course_id": ["Course1", "Course2"],
                "course_name": ["CourseName1", "CourseName2"],
                "day": ["SEG,QUA", "TER"],
                "time": ["08:00-10:00", "10:00-12:00"],
                "capacity": [30, 30],
                "classroom_type": ["Laboratório", "Sala"],
                "blackboard_restriction": ["FALSE", False],
            },
            index=[
                "OBG-BCC1-1",
                "OBG-BCC1-2",
            ],
        )

        section_allocation.index.name = "course_class_id"

        result = transform_sections_to_dict(section_allocation)

        expected_result = {
            "OBG-BCC1-1": {
                "institute": "IC",
                "professor": "Prof1",
                "course_id": "Course1",
                "course_name": "CourseName1",
                "day": "SEG,QUA",
                "time": "08:00-10:00",
                "capacity": 30,
                "classroom_type": "Laboratório",
                "blackboard_restriction": False,
            },
            "OBG-BCC1-2": {
                "institute": "IC",
                "professor": "Prof2",
                "course_id": "Course2",
                "course_name": "CourseName2",
                "day": "TER",
                "time": "10:00-12:00",
                "capacity": 30,
                "classroom_type": "Sala",
                "blackboard_restriction": False,
            },
        }

        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    main()
