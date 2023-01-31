import sqlmodel

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException

from src import authentication
from src import database


def db_conn():
    def db():
        with sqlmodel.Session(database.engine) as db:
            yield db

    return db


def authenticate(req: Request) -> bool:

    access_key = req.headers.get("Authorization")
    if not access_key:
        raise HTTPException(status_code=403)

    if authentication.is_access_key_valid(access_key):
        return True

    raise HTTPException(status_code=401)
