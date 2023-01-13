from datetime import datetime
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
from typing import Union

from database import query_to_csv_stream


router = APIRouter()


@router.get("/records")
async def get_records(
    response: Response,
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

    stream = query_to_csv_stream(query)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=records_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.csv"

    return response
