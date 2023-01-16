from datetime import datetime
from fastapi import APIRouter, Query
from typing import Union
from uuid import uuid1


from database import query_to_csv_stream
from cloud_storage import upload_to_cloud_storage


router = APIRouter()


@router.get("/records")
async def get_records(
    lat_max: float = 90,
    lat_min: float = -90,
    lon_max: float = 180,
    lon_min: float = -180,
    timestamp_from: Union[datetime, None] = None,
    timestamp_to: Union[datetime, None] = None,
    satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None),
    flags: Union[str, None] = Query(description="A comma separated list of the quality flag names", default=None),
):

    satellites_queries = ''
    if satellites:
        satellites = ','.join([f"'{satellite.strip()}'" for satellite in satellites.split(",")])
        satellites_queries = f'and s."name" in ({satellites})'

    flags_queries = ''
    if flags:
        flags = ','.join([f"'{flag.strip()}'" for flag in flags.split(",")])
        flags_queries = f'and q.name in ({flags})'

    timestamp_from_query = ''
    if timestamp_from:
        timestamp_from_query = f"""and r."timestamp" >= '{timestamp_from}'"""

    timestamp_to_query = ''
    if timestamp_to:
        timestamp_to_query = f"""and r."timestamp" <= '{timestamp_to}'"""

    query = f"""
    select  s.name as satellite, ST_X(r.point) as longitude, ST_Y(r.point) as latitude, r."timestamp", r.wind_direction, r.wind_speed, q."name", v."name" as version
    from record r
    join satellite s on r.satellite_id = s.id
    join qualityflag q on r.quality_flag_id = q.id
    join "version" v on r.version_id = v.id
    where ST_Intersects(ST_MakeEnvelope({lon_min}, {lat_min}, {lon_max}, {lat_max}), r.point) {satellites_queries} {flags_queries} {timestamp_from_query} {timestamp_to_query}
    """

    df, stream = query_to_csv_stream(query)
    download_url = None
    quota_used_bytes = None
    if df.empty is False:
        blob_client = upload_to_cloud_storage(f"{uuid1().hex}.csv", file_stream=stream.getvalue())
        download_url = blob_client.url
        quota_used_bytes = blob_client.get_blob_properties().size

    response_payload = {
        "download_url": download_url,
        "quota_used_bytes": quota_used_bytes,
        "records_count": df.shape[0]
    }

    return response_payload
