import pydantic

from datetime import datetime
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
        print(area)
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

            query = self.__query(url_params, count=True)

            data = {"total_records_count": database.raw_query(query).one()[0]}

            return responses.build_response(data=data)

        @self.get("/records")
        async def get_records(
            url_params: GetRecordsUrlParams = Depends(),
            is_authenticated: str = Depends(dependencies.authenticate),
        ):

            query = self.__query(
                url_params,
                count=False,
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
            return ""
        satellites = ",".join(
            [f"'{satellite.strip()}'" for satellite in satellites.split(",")]
        )
        return f'and s."name" in ({satellites})'

    def __flags_queries(self, flags):
        if not flags:
            return ""
        flags = ",".join([f"'{flag.strip()}'" for flag in flags.split(",")])
        return f"and q.name in ({flags})"

    def __timestamp_from_query(self, timestamp_from):
        if not timestamp_from:
            return ""
        return f"""and r."timestamp" >= '{timestamp_from}'"""

    def __timestamp_to_query(self, timestamp_to):
        if not timestamp_to:
            return ""
        return f"""and r."timestamp" <= '{timestamp_to}'"""

    def __time_interval_from_hours_query(self, time_interval_from_hours):
        if not time_interval_from_hours:
            return ""
        return f"""and r."timestamp" >= NOW() - INTERVAL '{time_interval_from_hours} HOURS'"""

    def __query(
        self,
        url_params,
        count=False,
    ):

        satellites_queries = self.__satellites_queries(url_params.satellites)
        flags_queries = self.__flags_queries(url_params.flags)
        timestamp_from_query = self.__timestamp_from_query(url_params.timestamp_from)
        timestamp_to_query = self.__timestamp_to_query(url_params.timestamp_to)
        time_interval_from_hours_query = self.__time_interval_from_hours_query(
            url_params.time_interval_from_hours
        )

        order_by = ""
        if count is True:
            select = "count(*)"
        else:
            select = 's.name as satellite, ST_X(r.point) as longitude, ST_Y(r.point) as latitude, r."timestamp", r.wind_direction, r.wind_speed, q."name", v."name" as version'
            order_by = 'order by r."timestamp" desc'

        query = f"""
        select {select}
        from record r
        join satellite s on r.satellite_id = s.id
        join qualityflag q on r.quality_flag_id = q.id
        left join "version" v on r.version_id = v.id
        where ST_Intersects(ST_MakeEnvelope({url_params.lon_min}, {url_params.lat_min}, {url_params.lon_max}, {url_params.lat_max}), r.point) {satellites_queries} {flags_queries} {timestamp_from_query} {timestamp_to_query} {time_interval_from_hours_query}
        {order_by}
        """

        return query
