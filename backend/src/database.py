from os import getenv
from sqlmodel import SQLModel, create_engine


# Engine
sqlite_url = getenv("DATABASE_URL")
engine = create_engine(sqlite_url)


# Create the models
def create_tables():
    SQLModel.metadata.create_all(engine)

