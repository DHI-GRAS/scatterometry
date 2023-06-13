import sqlmodel

from fastapi import Security
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException

from src import authentication
from src import database


def db_conn():
    def db():
        with sqlmodel.Session(database.engine) as db:
            yield db

    return db


def authenticate(
    api_key: str = Security(APIKeyHeader(name="Authorization", auto_error=True))
) -> bool:
    if not api_key:
        raise HTTPException(status_code=403)

    if authentication.is_access_key_valid(api_key):
        return True

    raise HTTPException(status_code=401)
