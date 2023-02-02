import pydantic

from datetime import datetime
from fastapi import Query
from typing import Union

from src import config


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

    @pydantic.validator("time_interval_from_hours")
    def temporal_logical_restrictions(cls, v, values):

        if v and (values["timestamp_from"] or values["timestamp_to"]):
            raise ValueError("Specify a temporal range or a time interval, not both")

        return v


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
