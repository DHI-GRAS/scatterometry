from fastapi import FastAPI, Query
from sqlalchemy import func
from typing import Union

import models


app = FastAPI()


@app.get("/records")
async def get_model(
    lat_max: float = 90,
    lat_min: float = -90,
    lon_max: float = 180,
    lon_min: float = -180,
    satellites: Union[str, None] = Query(description="A comma separated list of the satellite names", default=None)
):

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

    records = models.Record.filter(
        *filters
    )
    print(len(records))

    return 1
