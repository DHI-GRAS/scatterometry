from os import getenv, environ


CORS_ORIGINS = ["http://localhost", "http://localhost:8080",] + getenv(
    "CORS_ORIGINS_COMMA_SEP_LIST", ""
).split(",")


# DATABASE
DATABASE_URL = environ["DATABASE_URL"]


# AUTHENTICATION
ACCESS_KEYS = [key.strip() for key in getenv("ACCESS_KEYS", "").split(",")]


# BLOB STORAGE
AZURE_STORAGE_CONNECTION_STRING = environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_STORAGE_BLOB_CONTAINER = getenv("AZURE_STORAGE_BLOB_CONTAINER", "queryresults")


# REQUEST LIMITS
MAX_TIMESTAMP_DURATION_HOURS = int(getenv("MAX_TIMESTAMP_DURATION_HOURS", 24*31))
MAX_AREA_DEGREES = int(getenv("MAX_AREA_DEGREES", 20 * 44))
