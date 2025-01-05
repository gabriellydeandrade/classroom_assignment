from typing import Dict
import pandas as pd
from re import search
from numbers import Number
import numpy as np


def transform_sections_to_dict(data: pd.DataFrame) -> Dict:
    data = data.replace({np.nan: None})
    data_transformed = data.to_dict("index")
    key_to_delete = []
    for dt in data_transformed:
        capacity = 0
        line = data_transformed[dt]

        try:
            if "capacity" in line and line["capacity"]:
                capacity = int(line["capacity"])
        except ValueError:
            pass

        data_transformed[dt]["capacity"] = capacity

        if not isinstance(line["classroom_type"], str):
            line["classroom_type"] = None

        if line["classroom_type"] and search(r"[PT](,[PT])*", line["classroom_type"]):
            line["classroom_type"] = line["classroom_type"].replace("T", "Teórica")
            line["classroom_type"] = line["classroom_type"].replace("P", "Prática")

        if line["classroom_type"] == None:
            line["classroom_type"] = "NAO INFORMADO"

        if line["day"] == None or line["time"] == None:
            key_to_delete.append(dt)

        if line["blackboard_restriction"] == "FALSE":
            line["blackboard_restriction"] = False
        elif line["blackboard_restriction"] == "TRUE":
            line["blackboard_restriction"] = True

    for k in key_to_delete:
        del data_transformed[k]

    return data_transformed


def transform_classrooms_to_dict(data: pd.DataFrame) -> Dict:
    data = data.replace({np.nan: None})
    data_transformed = data.to_dict("index")

    for dt in data_transformed:
        capacity = 0
        line = data_transformed[dt]

        try:
            if "capacity" in line and line["capacity"]:
                capacity = int(line["capacity"])
            elif "capacity_siga" in line and line["capacity_siga"]:
                capacity = int(line["capacity_siga"])
        except ValueError:
            pass

        if line["capacity"] == 0 and line["capacity_siga"]:
            capacity = line["capacity_siga"]

        data_transformed[dt]["capacity"] = capacity

        if not isinstance(line["classroom_type"], str):
            line["classroom_type"] = None

        if line["classroom_type"] == None:
            line["classroom_type"] = "NAO INFORMADO"

    return data_transformed
