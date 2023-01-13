from os import getenv, environ


CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
] + getenv("CORS_ORIGINS_COMMA_SEP_LIST", "").split(",")


# DATABASE
DATABASE_URL = environ["DATABASE_URL"]
