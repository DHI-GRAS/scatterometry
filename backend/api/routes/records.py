from fastapi import APIRouter, Query, Depends
from geoalchemy2.shape import to_shape
from sqlmodel import Session, select
from sqlalchemy import func
from typing import Union, List

import models
import dependencies


router = APIRouter()


@router.get("/records")
async def get_records(
    lat_max: float = 90,
    lat_min: float = -90,
    lon_max: float = 180,
    lon_min: float = -180,
    satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None),
    db: Session = Depends(dependencies.db_conn()),
):

    records = get_records(db, lat_max, lat_min, lon_max, lon_min, satellites)
    print(records)
    csv_text = create_csv(records)

    return csv_text


def get_records(db: Session, lat_max, lat_min, lon_max, lon_min, satellites,):

    join = select(
        models.Record,
        models.Satellite
    ).join(models.Satellite)

    spatial_filter = [
        func.ST_Intersects(
            f"POLYGON(({lon_max} {lat_max}, {lon_min} {lat_max}, {lon_min} {lat_min}, {lon_max} {lat_min}, {lon_max} {lat_max}))",
            models.Record.point
        )
    ]

    satellites_filter = []
    if satellites:
        satellites_filter = [models.Satellite.name.in_(satellites.split(","))]

    filters = spatial_filter + satellites_filter

    return db.exec(join.where(*filters)).all()


def create_csv(records: List):
    csv_text = "longitude,latitude,wind_speed,satellite,wind_direction,wind_speed,flag,version" + "\n"
    for record, satellite in records:
        point = to_shape(record.point)
        row = (
            f"{point.x},{point.y},{record.timestamp},"
            f"{satellite.name},"
            f"{record.wind_direction},{record.wind_speed},"
            f"{record.quality_flag.flag},{record.version.name}"
            "\n"
        )
        csv_text = csv_text + row

    return csv_text
