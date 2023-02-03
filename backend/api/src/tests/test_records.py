import pytest

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src import app, config

client = TestClient(app.app)


DEFAULT_BBOX = {
    "lon_min": -10 * 0.25,
    "lat_min": -(config.MAX_AREA_DEGREES / 10) * 0.25,
    "lon_max": 10 * 0.75,
    "lat_max": (config.MAX_AREA_DEGREES / 10) * 0.75,
}


@pytest.mark.parametrize(
    "time_interval_from_hours, expected_status_code",
    [
        (None, 400),
        (-1, 400),
        (config.MAX_TIMESTAMP_DURATION_HOURS, 200),
        (config.MAX_TIMESTAMP_DURATION_HOURS + 1, 400),
    ],
)
def test_get_records_since_time_interval(
    time_interval_from_hours, expected_status_code
):
    params = {
        "time_interval_from_hours": time_interval_from_hours,
        **DEFAULT_BBOX,
    }

    response = client.get(
        "/records",
        params=params,
        headers={"Authorization": config.ACCESS_KEYS[0]},
    )

    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "timestamp_from, timestamp_to, expected_status_code",
    [
        (None, None, 400),
        ("Random string", 1, 400),
        (None, datetime.now().isoformat(), 400),
        (
            (
                datetime.now() - timedelta(hours=config.MAX_TIMESTAMP_DURATION_HOURS)
            ).isoformat(),
            datetime.now().isoformat(),
            200,
        ),
    ],
)
def test_get_records_in_time_range(timestamp_from, timestamp_to, expected_status_code):
    params = {
        "timestamp_from": timestamp_from,
        "timestamp_to": timestamp_to,
        **DEFAULT_BBOX,
    }

    response = client.get(
        "/records",
        params=params,
        headers={"Authorization": config.ACCESS_KEYS[0]},
    )

    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "lon_min, lat_min, lon_max, lat_max, expected_status_code",
    [
        (None, None, None, None, 400),
        (None, "Random string", None, 1, 400),
        (DEFAULT_BBOX["lon_min"], DEFAULT_BBOX["lat_min"], DEFAULT_BBOX["lon_max"] + 1, DEFAULT_BBOX["lat_max"] + 1, 400),
        (tuple(DEFAULT_BBOX.values())) + (200,),
    ],
)
def test_get_records_in_time_range(lon_min, lat_min, lon_max, lat_max, expected_status_code):
    params = {
        "timestamp_from": (datetime.now() - timedelta(hours=config.MAX_TIMESTAMP_DURATION_HOURS)).isoformat(),
        "timestamp_to": datetime.now().isoformat(),
        "lon_min": lon_min,
        "lat_min": lat_min,
        "lon_max": lon_max,
        "lat_max": lat_max,
    }

    response = client.get(
        "/records",
        params=params,
        headers={"Authorization": config.ACCESS_KEYS[0]},
    )

    assert response.status_code == expected_status_code
