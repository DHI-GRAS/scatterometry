from os import environ
from sqlmodel import create_engine

import crud


def main():
    engine = create_engine(environ["DATABASE_URL"], echo=False, future=False)
    mission = crud.create_mission(engine, "mission")

    sattelites = [
        {
            "name": "rscat",
            "is_active": True,
            "wind_direction_correction": 0.0,
        },
        {
            "name": "cygnss",
            "is_active": True,
            "wind_direction_correction": 0.0,
        },
        {
            "name": "oscat",
            "is_active": True,
            "wind_direction_correction": 0.0,
        },
        {
            "name": "qscat",
            "is_active": True,
            "wind_direction_correction": 0.0,
        },
        {
            "name": "ascat",
            "is_active": True,
            "wind_direction_correction": 0.0,
        },
    ]
    quality_flags = [
        {
            "flag": "0",
            "name": "good",
            "description": "good",
        },
        {
            "flag": "1",
            "name": "bad",
            "description": "bad",
        },
        {
            "flag": "2",
            "name": "suspect",
            "description": "suspect",
        },
        {
            "flag": "3",
            "name": "medium",
            "description": "medium",
        },
    ]
    for satellite_data in sattelites:
        satellite = crud.create_satellite(
            engine,
            mission=mission,
            name=satellite_data["name"],
            is_active=satellite_data["is_active"],
            wind_direction_correction=satellite_data["wind_direction_correction"],
        )
        for quality_flag_data in quality_flags:
            quality_flag = crud.create_quality_flag(
                engine,
                satellite=satellite,
                flag=quality_flag_data["flag"],
                name=quality_flag_data["name"],
                description=quality_flag_data["description"],
            )


if __name__ == "__main__":
    main()
