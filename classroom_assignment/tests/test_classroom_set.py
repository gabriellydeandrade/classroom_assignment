from unittest import TestCase, main
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # FIXME quero corrigir de outra forma

from database.service_google_sheet import get_classrooms_available
from database.transform_data import transform_to_dict
import pandas as pd


class TestClassroomAvailableFromGoogleSheets(TestCase):

    # @patch.object(cache_to_csv, "cache_to_csv")
    @patch("database.service_google_sheet.cache_to_csv")
    @patch("database.service_google_sheet.read_google_sheet_to_dataframe")
    # @patch("cache_pandas.cache_to_csv", lambda *args, **kwargs: lambda func: func)
    def test_get_classrooms_available(self, mock_read_google_sheet, temp):
        temp.return_value.return_value = Mock()

        mock_data = pd.DataFrame(
            {
                "Disponível": ["TRUE", "TRUE"],
                "Nome": ["Sala 1", "Sala 2"],
                "Instituto responsável": ["IC", "IC"],
                "Tipo sala": ["Laboratório", "Sala"],
                "Capacidade real": [30, 30],
                "Capacidade SIGA": [40, 40],
            },
        )

        mock_data.index.name = "course_class_id"

        mock_read_google_sheet.return_value = mock_data

        result = get_classrooms_available()

        expected_data = pd.DataFrame(
            {
                "responsable_institute": ["IC", "IC"],
                "classroom_type": ["Laboratório", "Sala"],
                "capacity_siga": [40, 40],
                "capacity": [30, 30],
            },
            index=[
                "Sala 1",
                "Sala 2",
            ],
        )

        expected_data.index.name = "classroom_name"

        mock_read_google_sheet.assert_called_once()
        pd.testing.assert_frame_equal(result, expected_data)


class TestTransformClassroomAvailable(TestCase):

    def test_treat_classroom_available_with_correct_params(self):
        classrom_available = pd.DataFrame(
            {
                "classroom_name": ["Sala 1", "Sala 2"],
                "responsible_institute": ["IC", "IC"],
                "classrom_type": ["Laboratório", "Sala"],
                "capacity": [30, 30],
            },
            index=[
                "Sala 1",
                "Sala 2",
            ],
        )

        classrom_available.index.name = "classroom_name"

        result = transform_to_dict(classrom_available)

        expected_result = {
            "Sala 1": {
                "classroom_name": "Sala 1",
                "responsible_institute": "IC",
                "classrom_type": "Laboratório",
                "capacity": 30,
            },
            "Sala 2": {
                "classroom_name": "Sala 2",
                "responsible_institute": "IC",
                "classrom_type": "Sala",
                "capacity": 30,
            },
        }

        self.assertDictEqual(result, expected_result)

    def test_treat_classroom_with_capacity_from_siga_when_real_capacity_is_empty(self):
        classrom_available = pd.DataFrame(
            {
                "classroom_name": ["Sala 1", "Sala 2"],
                "responsible_institute": ["IC", "IC"],
                "classrom_type": ["Laboratório", "Sala"],
                "capacity_siga": [40, 40],
                "capacity": ["", 30],
            },
            index=[
                "Sala 1",
                "Sala 2",
            ],
        )

        classrom_available.index.name = "classroom_name"

        result = transform_to_dict(classrom_available)

        expected_result = {
            "Sala 1": {
                "classroom_name": "Sala 1",
                "responsible_institute": "IC",
                "classrom_type": "Laboratório",
                "capacity_siga": 40,
                "capacity": 40,
            },
            "Sala 2": {
                "classroom_name": "Sala 2",
                "responsible_institute": "IC",
                "classrom_type": "Sala",
                "capacity_siga": 40,
                "capacity": 30,
            },
        }

        self.assertDictEqual(result, expected_result)

    def test_treat_classroom_with_zero_capacity_when_capacity_is_not_set(self):
        classrom_available = pd.DataFrame(
            {
                "classroom_name": ["Sala 1", "Sala 2"],
                "responsible_institute": ["IC", "IC"],
                "classrom_type": ["Laboratório", "Sala"],
                "capacity_siga": ["", ""],
                "capacity": ["", ""],
            },
            index=[
                "Sala 1",
                "Sala 2",
            ],
        )

        classrom_available.index.name = "classroom_name"

        result = transform_to_dict(classrom_available)

        expected_result = {
            "Sala 1": {
                "classroom_name": "Sala 1",
                "responsible_institute": "IC",
                "classrom_type": "Laboratório",
                "capacity_siga": "",
                "capacity": 0,
            },
            "Sala 2": {
                "classroom_name": "Sala 2",
                "responsible_institute": "IC",
                "classrom_type": "Sala",
                "capacity_siga": "",
                "capacity": 0,
            },
        }

        self.assertDictEqual(result, expected_result)

if __name__ == "__main__":
    main()
