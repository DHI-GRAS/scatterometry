from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlmodel

from src.authentication import validate_token
from src.database import engine


def db_conn():
    def db():
        with sqlmodel.Session(engine) as db:
            yield db

    return db


def authenticate(
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> str:
    uid = validate_token(authorization.credentials)
    return uid
