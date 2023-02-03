from os import environ
from psycopg2.extensions import register_adapter, AsIs
from shapely.geometry.point import Point
from sqlmodel import create_engine, Session, select

from scatterometry_database import models


# DATABASE
engine = create_engine(environ["DATABASE_URL"], echo=False, future=False)


# ADAPTERS
def adapt_geometry_point(point):
    return AsIs(repr(point.wkt))


register_adapter(Point, adapt_geometry_point)


# CRUD
def read_record_file(filename):
    with Session(engine) as session:
        statement = select(models.RecordFile).where(
            models.RecordFile.filename == filename
        )
        file_records = session.exec(statement).first()
    return file_records


def delete_record_file(record_file):
    with Session(engine) as session:
        session.delete(record_file)
        session.commit()


def create_record_file(filename, checksum):
    with Session(engine) as session:
        record_file = models.RecordFile(filename=filename, checksum=checksum)
        session.add(record_file)
        session.commit()
        session.refresh(record_file)
    return record_file


def read_satellite(satellite_name):
    with Session(engine) as session:
        statement = select(models.Satellite).where(
            models.Satellite.name == satellite_name
        )
        satellites = session.exec(statement).one()
    return satellites


def read_quality_flags(satellite_id):
    with Session(engine) as session:
        quality_flag = select(models.QualityFlag).where(
            models.QualityFlag.satellite_id == satellite_id
        )
        quality_flag = session.exec(quality_flag).all()
    return quality_flag


def read_quality_flag(satellite_id, flag):
    with Session(engine) as session:
        quality_flag = select(models.QualityFlag).where(
            models.QualityFlag.satellite_id == satellite_id,
            models.QualityFlag.flag == flag,
        )
        quality_flag = session.exec(quality_flag).one()
    return quality_flag


def read_latest_satellite_record(satellite, offset=0, limit=1):
    with Session(engine) as session:
        statement = (
            select(models.Record)
            .where(models.Record.satellite_id == satellite.id)
            .order_by(models.Record.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        record = session.exec(statement).first()
    return record


def read_earliest_satellite_record(satellite, offset=0, limit=1):
    with Session(engine) as session:
        statement = (
            select(models.Record)
            .where(models.Record.satellite_id == satellite.id)
            .order_by(models.Record.timestamp.asc())
            .offset(offset)
            .limit(limit)
        )
        record = session.exec(statement).first()
    return record


def write_records_from_data_frame(data_frame):
    data_frame.to_sql(
        models.Record.__table__.name,
        engine,
        if_exists="append",
        index=False,
        chunksize=1000,
    )


def delete_records_of_file(record_file: models.RecordFile):
    with Session(engine) as session:
        statement = models.Record.__table__.delete().where(
            models.Record.record_file_id == record_file.id
        )
        session.exec(statement)
        session.commit()


def raw_query(query):
    with engine.connect() as connection:
        result = connection.execute(query)
        return result
