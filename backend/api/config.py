from sqlmodel import create_engine

from os import getenv, environ


CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
] + getenv("CORS_ORIGINS_COMMA_SEP_LIST", "").split(",")


# DATABASE
engine = create_engine(environ["DATABASE_URL"], echo=False, future=False)
