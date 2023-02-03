import geoalchemy2
import sqlalchemy

from datetime import datetime, timedelta

from scatterometry_database import models
from src import (
    database,
)


def __satellites_queries(satellites):
    if not satellites:
        return None
    satellites = ",".join(
        [f"'{satellite.strip()}'" for satellite in satellites.split(",")]
    )
    return models.Satellite.name.in_(satellites)


def __flags_queries(flags):
    if not flags:
        return None
    flags = ",".join([f"'{flag.strip()}'" for flag in flags.split(",")])
    return models.QualityFlag.name.in_(flags)


def __timestamp_from_query(timestamp_from):
    if not timestamp_from:
        return None
    return models.Record.timestamp >= timestamp_from.isoformat()


def __timestamp_to_query(timestamp_to):
    if not timestamp_to:
        return None
    return models.Record.timestamp <= timestamp_to.isoformat()


def __time_interval_from_hours_query(time_interval_from_hours):
    if not time_interval_from_hours:
        return None
    return (
        models.Record.timestamp
        >= (datetime.now() - timedelta(hours=time_interval_from_hours)).isoformat()
    )


def __query(
    url_params,
):

    query_filters = [
        __satellites_queries(url_params.satellites),
        __flags_queries(url_params.flags),
        __timestamp_from_query(url_params.timestamp_from),
        __timestamp_to_query(url_params.timestamp_to),
        __time_interval_from_hours_query(url_params.time_interval_from_hours),
    ]

    with database.Session() as session:

        query = (
            session.query(
                models.Satellite.name.label("satellite"),
                geoalchemy2.func.st_x(models.Record.point).label("longitude"),
                geoalchemy2.func.st_y(models.Record.point).label("latitude"),
                models.Record.timestamp.label("timestamp"),
                models.Record.wind_direction,
                models.Record.wind_speed,
                models.QualityFlag.name.label("quality_flag"),
                models.Version.name.label("version"),
            )
            .join(
                models.Record.satellite,
                models.Record.quality_flag,
            )
            .join(
                models.Record.version,
                isouter=True,
            )
            .filter(
                models.Record.point.intersects(
                    geoalchemy2.func.ST_MakeEnvelope(
                        url_params.lon_min,
                        url_params.lat_min,
                        url_params.lon_max,
                        url_params.lat_max,
                    ),
                ),
                *[qf for qf in query_filters if qf is not None],
            )
        )

    return query


def count_query_records(url_params):
    query = __query(url_params)
    return query.with_entities(sqlalchemy.func.count()).scalar()


def get_query_string(url_params):
    sqlalchemy_query = __query(url_params)
    return str(
        sqlalchemy_query.statement.compile(
            dialect=sqlalchemy.dialects.postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
