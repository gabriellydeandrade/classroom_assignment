from typing import Dict
import pandas as pd
from re import search
from numbers import Number


def transform_to_dict(data: pd.DataFrame) -> Dict:
    data_transformed = data.to_dict("index")

    for dt in data_transformed:
        capacity = 0
        line = data_transformed[dt]

        if "capacity" in line and (not isinstance(line["capacity"], Number) or line["capacity"] < 0): 
            line["capacity"] = None
        if "capacity_siga" in line and (not isinstance(line["capacity_siga"], Number) or line["capacity_siga"] < 0):
            line["capacity_siga"] = None

        try:
            if "capacity" in line and line["capacity"]:
                capacity = int(line["capacity"])
            elif "capacity_siga" in line and line["capacity_siga"]:
                capacity = int(line["capacity_siga"])
        except ValueError:
            pass

        data_transformed[dt]["capacity"] = capacity

        if not isinstance(line["classroom_type"], str): 
            line["classroom_type"] = None

        if line["classroom_type"] and search(r"[PT](,[PT])*", line["classroom_type"]):
            line["classroom_type"] = line["classroom_type"].replace("T", "Sala")
            line["classroom_type"] = line["classroom_type"].replace("P", "Laboratório")

    return data_transformed
