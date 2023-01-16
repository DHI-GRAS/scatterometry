import io
import pandas as pd

from sqlmodel import create_engine

import config


engine = create_engine(config.DATABASE_URL, echo=False, future=False)


def raw_query(query):
    with engine.connect() as connection:
        result = connection.execute(query)
        return result


def query_to_df(query):
    df = pd.read_sql_query(query, con=engine)
    return df


def query_to_csv_stream(query, index=False, header=True, sep=",", quotechar='"', no_data=None):
    stream = io.StringIO()
    df = query_to_df(query)
    df.to_csv(stream, index=index, header=header, sep=sep, quotechar=quotechar, na_rep=no_data)
    return df, stream
