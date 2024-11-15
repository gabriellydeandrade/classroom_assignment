from typing import Dict
import pandas as pd


def transform_to_dict(data: pd.DataFrame) -> Dict:
    data_transformed = data.to_dict("index")

    for dt in data_transformed:
        capacity = 0

        try:
            if "capacity" in data_transformed[dt] and data_transformed[dt]["capacity"]:
                capacity = int(data_transformed[dt]["capacity"])
            elif "capacity_siga" in data_transformed[dt] and data_transformed[dt]["capacity_siga"]:
                capacity = int(data_transformed[dt]["capacity_siga"])
        except ValueError:
            pass

        data_transformed[dt]["capacity"] = capacity

    return data_transformed
