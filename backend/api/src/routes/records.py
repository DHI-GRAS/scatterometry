import pydantic
import geoalchemy2
import sqlalchemy

from datetime import datetime, timedelta
from fastapi import APIRouter, Query, Depends
from typing import Union
from uuid import uuid1

from src import (
    cloud_storage,
    config,
    database,
    dependencies,
    responses,
    models,
)


class RecordsUrlParams(pydantic.BaseModel):

    lat_max: float = 90
    lat_min: float = -90
    lon_max: float = 360
    lon_min: float = 0
    timestamp_to: Union[datetime, None] = None
    timestamp_from: Union[datetime, None] = None
    time_interval_from_hours: int = None
    satellites: Union[str, None] = pydantic.Field(
        Query(description="A comma separated list of the satellite names", default=None)
    )
    flags: Union[str, None] = pydantic.Field(
        Query(
            description="A comma separated list of the quality flag names", default=None
        )
    )


class GetRecordsUrlParams(RecordsUrlParams):
    @pydantic.validator("lon_min")
    def spatial_area(cls, v, values):
        area = (values["lon_max"] - v) * (values["lat_max"] - values["lat_min"])
        if area > config.MAX_AREA_DEGREES:
            raise ValueError(
                f"Spatial area can not be greater than {config.MAX_AREA_DEGREES} square degrees"
            )
        return v

    @pydantic.validator("time_interval_from_hours")
    def temporal_logical_restrictions(cls, v, values):
        if not v and not (values["timestamp_from"] or values["timestamp_to"]):
            raise ValueError("Specify a temporal range or a time interval")

        if v and (values["timestamp_from"] or values["timestamp_to"]):
            raise ValueError("Specify a temporal range or a time interval, not both")

        if not v and not (values["timestamp_from"] and values["timestamp_to"]):
            raise ValueError(
                "For a temporal range specify both limits, timestamp_from and timestamp_to"
            )
        return v

    @pydantic.validator("time_interval_from_hours")
    def temporal_duration_of_range(cls, v, values):
        if not (values["timestamp_from"] and values["timestamp_to"]):
            return v
        time_diff = values["timestamp_to"] - values["timestamp_from"]
        if (
            time_diff.days * 24 + time_diff.seconds / 3600
        ) > config.MAX_TIMESTAMP_DURATION_HOURS:
            raise ValueError(
                f"Temporal range duration can not be greater than {config.MAX_TIMESTAMP_DURATION_HOURS} hours"
            )
        return v

    @pydantic.validator("time_interval_from_hours")
    def temporal_duration_of_interval(cls, value):
        if value and value > config.MAX_TIMESTAMP_DURATION_HOURS:
            raise ValueError(
                f"Temporal query interval can not be greater than {config.MAX_TIMESTAMP_DURATION_HOURS} hours"
            )
        return value


class ProjectsRoute(APIRouter):
    def __init__(self) -> None:
        super().__init__()

        @self.get("/records/count")
        async def get_records(
            url_params: RecordsUrlParams = Depends(),
            is_authenticated: str = Depends(dependencies.authenticate),
        ):

            query = self.__query(url_params)

            data = {
                "total_records_count": query.with_entities(
                    sqlalchemy.func.count()
                ).scalar()
            }

            return responses.build_response(data=data)

        @self.get("/records")
        async def get_records(
            url_params: GetRecordsUrlParams = Depends(),
            is_authenticated: str = Depends(dependencies.authenticate),
        ):

            sqlalchemy_query = self.__query(
                url_params,
            )
            query = str(
                sqlalchemy_query.statement.compile(
                    dialect=sqlalchemy.dialects.postgresql.dialect(),
                    compile_kwargs={"literal_binds": True},
                )
            )

            df, stream = database.query_to_csv_stream(query)
            download_url = None
            quota_used_bytes = None
            if df.empty is False:
                blob_client = cloud_storage.upload_to_cloud_storage(
                    f"{uuid1().hex}.csv", file_stream=stream.getvalue()
                )
                download_url = blob_client.url
                quota_used_bytes = blob_client.get_blob_properties().size

            return responses.build_response(
                data={
                    "download_url": download_url,
                    "quota_used_bytes": quota_used_bytes,
                    "total_records_count": df.shape[0],
                }
            )

    def __satellites_queries(self, satellites):
        if not satellites:
            return None
        satellites = ",".join(
            [f"'{satellite.strip()}'" for satellite in satellites.split(",")]
        )
        return models.Satellite.name.in_(satellites)

    def __flags_queries(self, flags):
        if not flags:
            return None
        flags = ",".join([f"'{flag.strip()}'" for flag in flags.split(",")])
        return models.QualityFlag.name.in_(flags)

    def __timestamp_from_query(self, timestamp_from):
        if not timestamp_from:
            return None
        return models.Record.timestamp >= timestamp_from.isoformat()

    def __timestamp_to_query(self, timestamp_to):
        if not timestamp_to:
            return None
        return models.Record.timestamp <= timestamp_to.isoformat()

    def __time_interval_from_hours_query(self, time_interval_from_hours):
        if not time_interval_from_hours:
            return None
        return (
            models.Record.timestamp
            >= (datetime.now() - timedelta(hours=time_interval_from_hours)).isoformat()
        )

    def __query(
        self,
        url_params,
    ):

        query_filters = [
            self.__satellites_queries(url_params.satellites),
            self.__flags_queries(url_params.flags),
            self.__timestamp_from_query(url_params.timestamp_from),
            self.__timestamp_to_query(url_params.timestamp_to),
            self.__time_interval_from_hours_query(url_params.time_interval_from_hours),
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
