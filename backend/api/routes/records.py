from fastapi import APIRouter, Query
from geoalchemy2.shape import to_shape
from sqlalchemy import func
from typing import Union, List

import models


router = APIRouter()


@router.get("/records")
async def get_records(
    lat_max: float = 90,
    lat_min: float = -90,
    lon_max: float = 180,
    lon_min: float = -180,
    satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None)
):

    records = get_records(lat_max, lat_min, lon_max, lon_min, satellites)
    csv_text = create_csv(records)

    return csv_text


def get_records(lat_max, lat_min, lon_max, lon_min, satellites,):

    spatial_filter = [
        func.ST_Intersects(
            f"POLYGON(({lon_max} {lat_max}, {lon_min} {lat_max}, {lon_min} {lat_min}, {lon_max} {lat_min}, {lon_max} {lat_max}))",
            models.Record.point
        )
    ]

    satellites_filter = []
    if satellites:
        satellite_items = [models.Satellite.get(models.Satellite.name == satellite) for satellite in satellites.split(',')]
        satellites_filter = [models.Record.satellite == satellite for satellite in satellite_items]

    filters = spatial_filter + satellites_filter

    return models.Record.filter(
        *filters
    )


def create_csv(records: List):
    csv_text = "longitude,latitude,wind_speed,satellite,wind_direction,wind_speed,flag,version" + "\n"
    for record in records:
        point = to_shape(record.point)
        satellite = models.Satellite.get(models.Satellite.id == record.satellite_id)
        quality_flag = models.QualityFlag.get(models.QualityFlag.id == record.quality_flag_id)
        version = models.Version.get(models.Version.id == record.version_id)
        row = (
            f"{point.x},{point.y},{record.timestamp},"
            f"{satellite.name},"
            f"{record.wind_direction},{record.wind_speed},"
            f"{quality_flag.flag},{version.name}"
            "\n"
        )
        csv_text = csv_text + row

    return csv_text
