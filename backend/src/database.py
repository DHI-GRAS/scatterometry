from os import getenv
from sqlmodel import SQLModel, Session, select, create_engine


class DatabaseModel(SQLModel):
    """
    A class that expends the original SQLModel class to include user friendly methods for
    making CRUD operations in the database from model instances
    """

    def create(self):
        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)
            return self

    def update(self, **kwargs):
        with Session(engine) as session:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.add(self)
            session.commit()
            session.refresh(self)
            return self

    def delete(self):
        with Session(engine) as session:
            session.delete(self)
            session.commit()
            return self

    def read_related(self, related_table):
        """
        Reads all model data from the database
        """

        with Session(engine) as session:
            self_item_in_session = session.exec(select(self.__class__).where(self.__class__.id == self.id)).one()
            return getattr(self_item_in_session, related_table)

    @classmethod
    def read(cls, offset:int=None, limit:int=None):
        """
        Reads all model data from the database
        """

        if offset is None:
            offset = 0
        if limit is None:
            limit = 1000

        with Session(engine) as session:
            return session.exec(select(cls).offset(offset).limit(limit)).all()

    @classmethod
    def get(cls, filtering_expression, exactly=True):
        """
        Gets one item from the database based on a search expression
        """
        with Session(engine) as session:
            query_result = session.exec(select(cls).where(filtering_expression))
            if exactly is True:
                return query_result.one()
            return query_result.first()

    @classmethod
    def filter(cls, filtering_expression, offset:int=None, limit:int=None):
        """
        Gets all items from the database that comply with the search expression
        """

        if offset is None:
            offset = 0
        if limit is None:
            limit = 1000

        with Session(engine) as session:
            return session.exec(select(cls).where(filtering_expression).offset(offset).limit(limit)).all()


# Engine
sqlite_url = getenv("DATABASE_URL")
engine = create_engine(sqlite_url)


# Create the models
def create_tables():
    SQLModel.metadata.create_all(engine)

