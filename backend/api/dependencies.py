
import sqlmodel

from database import engine


def db_conn():
    def db():
        with sqlmodel.Session(engine) as db:
            yield db

    return db
