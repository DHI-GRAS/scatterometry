import io
import pandas as pd
import sqlalchemy
import sqlmodel

from src import config


engine = sqlmodel.create_engine(config.DATABASE_URL, echo=False, future=False)

Session = sqlalchemy.orm.sessionmaker(bind=engine)


def raw_query(query):
    with engine.connect() as connection:
        result = connection.execute(query)
        return result


def query_to_df(query):
    for chunk in pd.read_sql_query(query, con=engine, chunksize=10000):
        yield chunk


def query_to_csv_stream(
    query, index=False, header=True, sep=",", quotechar='"', no_data=None
):
    stream = io.StringIO()
    df = pd.DataFrame()
    for chunk in query_to_df(query):
        df = pd.concat([df, chunk], ignore_index=True)
    df.to_csv(
        stream, index=index, header=header, sep=sep, quotechar=quotechar, na_rep=no_data
    )
    return df, stream
