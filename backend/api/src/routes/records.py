from datetime import datetime
from fastapi import APIRouter, Query
from typing import Union
from uuid import uuid1

import config

from database import query_to_csv_stream, raw_query
from cloud_storage import upload_to_cloud_storage


class ProjectsRoute(APIRouter):

    def __init__(self) -> None:
        super().__init__()

        @self.get("/records/count")
        async def get_records(
            lat_max: float = 90,
            lat_min: float = -90,
            lon_max: float = 360,
            lon_min: float = 0,
            timestamp_from: Union[datetime, None] = None,
            timestamp_to: Union[datetime, None] = None,
            time_interval_from: str = None,
            satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None),
            flags: Union[str, None] = Query(description="A comma separated list of the quality flag names", default=None),
        ):

            query = self.__query(lon_min, lat_min, lon_max, lat_max, satellites,
                flags, timestamp_from, timestamp_to, time_interval_from, count=True
            )

            total_records_count = raw_query(query).one()[0]

            response_payload = {
                "status": "success",
                "error": False,
                "message": None,
                "total_records_count": total_records_count,
            }

            return response_payload

        @self.get("/records")
        async def get_records(
            lat_max: float = 90,
            lat_min: float = -90,
            lon_max: float = 360,
            lon_min: float = 0,
            timestamp_from: Union[datetime, None] = None,
            timestamp_to: Union[datetime, None] = None,
            time_interval_from: str = None,
            satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None),
            flags: Union[str, None] = Query(description="A comma separated list of the quality flag names", default=None),
            page: int = Query(description="The pagination index. The pagination starts from 1", default=1),
        ):

            # Count all records for query
            total_records_query = self.__query(lon_min, lat_min, lon_max, lat_max, satellites,
                flags, timestamp_from, timestamp_to, time_interval_from, count=True
            )
            total_records_count = raw_query(total_records_query).one()[0]

            # Collect the records of the page
            if page < 1:
                page = 1
            query = self.__query(lon_min, lat_min, lon_max, lat_max, satellites, flags,
                timestamp_from, timestamp_to, time_interval_from, page, count=False,
            )

            df, stream = query_to_csv_stream(query)
            download_url = None
            quota_used_bytes = None
            if df.empty is False:
                blob_client = upload_to_cloud_storage(f"{uuid1().hex}.csv", file_stream=stream.getvalue())
                download_url = blob_client.url
                quota_used_bytes = blob_client.get_blob_properties().size

            response_payload = {
                "status": "success",
                "error": False,
                "message": None,
                "download_url": download_url,
                "quota_used_bytes": quota_used_bytes,
                "current_records_count": df.shape[0],
                "total_records_count": total_records_count,
            }

            return response_payload

    def __satellites_queries(self, satellites):
        if not satellites:
            return ""
        satellites = ','.join([f"'{satellite.strip()}'" for satellite in satellites.split(",")])
        return f'and s."name" in ({satellites})'

    def __flags_queries(self, flags):
        if not flags:
            return ""
        flags = ','.join([f"'{flag.strip()}'" for flag in flags.split(",")])
        return f'and q.name in ({flags})'

    def __timestamp_from_query(self, timestamp_from):
        if not timestamp_from:
            return ""
        return f"""and r."timestamp" >= '{timestamp_from}'"""

    def __timestamp_to_query(self, timestamp_to):
        if not timestamp_to:
            return ""
        return f"""and r."timestamp" <= '{timestamp_to}'"""

    def __time_interval_from_query(self, time_interval_from):
        if not time_interval_from:
            return ""
        return f"""and r."timestamp" >= NOW() - INTERVAL '{time_interval_from}'"""

    def __query(
        self,
        lon_min,
        lat_min,
        lon_max,
        lat_max,
        satellites,
        flags,
        timestamp_from,
        timestamp_to,
        time_interval_from,
        page=None,
        count=False,
    ):

        satellites_queries = self.__satellites_queries(satellites)
        flags_queries = self.__flags_queries(flags)
        timestamp_from_query = self.__timestamp_from_query(timestamp_from)
        timestamp_to_query = self.__timestamp_to_query(timestamp_to)
        time_interval_from = self.__time_interval_from_query(time_interval_from)

        limits = ""
        order_by = ""
        if count is True:
            select = "count(*)"
        else:
            select = 's.name as satellite, ST_X(r.point) as longitude, ST_Y(r.point) as latitude, r."timestamp", r.wind_direction, r.wind_speed, q."name", v."name" as version'
            order_by = 'order by r."timestamp" desc'
            limits = f"limit {config.RECORDS_PER_PAGE} offset {page * config.RECORDS_PER_PAGE - config.RECORDS_PER_PAGE}"

        query = f"""
        select {select}
        from record r
        join satellite s on r.satellite_id = s.id
        join qualityflag q on r.quality_flag_id = q.id
        left join "version" v on r.version_id = v.id
        where ST_Intersects(ST_MakeEnvelope({lon_min}, {lat_min}, {lon_max}, {lat_max}), r.point) {satellites_queries} {flags_queries} {timestamp_from_query} {timestamp_to_query} {time_interval_from}
        {order_by}
        {limits}
        """

        return query
