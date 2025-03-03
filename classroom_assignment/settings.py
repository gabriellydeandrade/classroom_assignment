from decouple import config
from enum import Enum

SAMPLE_SPREADSHEET_ID = config("SAMPLE_SPREADSHEET_ID", default="1DgpZucQbgYB-fjVUehGSdy8xXutAL_7CY6joRCrKVH8")

class LicenseType(Enum):
    NAMED_USER_ACADEMIC = "Named-User Academic"
    WSL_ACADEMIC = "WSL Academic"

APP_LICENSE_TYPE = config("LICENSE_TYPE", default=LicenseType.NAMED_USER_ACADEMIC.value, cast=lambda v: v if v in LicenseType._value2member_map_ else LicenseType.NAMED_USER_ACADEMIC.value)
APP_LICENSE_ID = config("LICENSE_ID", default=123, cast=int)
APP_WLS_ACCESS_ID = config("WLS_ACCESS_ID", default="access_id")
APP_WS_SECRET = config("WS_SECRET", default="secret")

APP_CACHE_TTL = config("CACHE_TTL", default=29809, cast=int)
