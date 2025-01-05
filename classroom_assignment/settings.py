from decouple import config

SAMPLE_SPREADSHEET_ID = config("SAMPLE_SPREADSHEET_ID", default="1DgpZucQbgYB-fjVUehGSdy8xXutAL_7CY6joRCrKVH8")

APP_LICENSE_ID = config("LICENSE_ID", default=123, cast=int)
APP_WLS_ACCESS_ID = config("WLS_ACCESS_ID", default="access_id")
APP_WS_SECRET = config("WS_SECRET", default="secret")

APP_CACHE_TTL = config("CACHE_TTL", default=989809, cast=int)
