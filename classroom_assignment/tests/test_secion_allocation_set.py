from unittest import TestCase, main
from unittest.mock import patch
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from database.service_google_sheet import (
    get_secion_allocation,
)
from database.transform_data import transform_to_dict


import pandas as pd


class TestSectionAllocationFromGoogleSheets(TestCase):
    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    def test_get_secion_allocation(self, mock_read_google_sheet):
        mock_data = pd.DataFrame(
            {
                "Instituto": ["IC", "IC"],
                "Código único turma": [
                    "OBG-BCC1-1",
                    "OBG-BCC1-2",
                ],
                "Nome curto professor": ["Prof1", "Prof2"],
                "Código disciplina": ["Course1", "Course2"],
                "Nome disciplina": ["CourseName1", "CourseName2"],
                "Dia da semana": ["SEG,QUA", "TER"],
                "Horário": ["08:00-10:00", "10:00-12:00"],
                "Qtd alunos": [30, 30],
                "Tipo sala": ["Laboratório", "Sala"],
            },
        )

        mock_data.index.name = "course_class_id"

        mock_read_google_sheet.return_value = mock_data

        result = get_secion_allocation()

        expected_data = pd.DataFrame(
            {
                "institute": ["IC", "IC"],
                "professor": ["Prof1", "Prof2"],
                "course_id": ["Course1", "Course2"],
                "course_name": ["CourseName1", "CourseName2"],
                "day": ["SEG,QUA", "TER"],
                "time": ["08:00-10:00", "10:00-12:00"],
                "capacity": [30, 30],
                "classroom_type": ["Laboratório", "Sala"],
            },
            index=[
                "OBG-BCC1-1",
                "OBG-BCC1-2",
            ],
        )

        expected_data.index.name = "course_class_id"


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
            },
            index=[
                "OBG-BCC1-1",
                "OBG-BCC1-2",
            ],
        )

        section_allocation.index.name = "course_class_id"

        result = transform_to_dict(section_allocation)

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
            },
        }

        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    main()
