from typing import Dict
import pandas as pd


def transform_to_dict(data: pd.DataFrame) -> Dict:
    data_transformed = data.to_dict("index")

    for dt in data_transformed:
        data_transformed[dt]["capacity"] = int(
            data_transformed[dt]["capacity"]
        )

    return data_transformed