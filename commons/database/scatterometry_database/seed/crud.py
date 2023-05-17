from sqlmodel import create_engine, Session

from scatterometry_database import models


def create_mission(engine, name):
    with Session(engine) as session:
        mission = models.Mission(name=name)
        session.add(mission)
        session.commit()
        session.refresh(mission)
    return mission


def create_satellite(engine, mission, name, is_active, wind_direction_correction):
    with Session(engine) as session:
        satellite = models.Satellite(mission=mission, name=name, is_active=is_active, wind_direction_correction=wind_direction_correction)
        session.add(satellite)
        session.commit()
        session.refresh(satellite)
    return satellite


def create_quality_flag(engine, satellite, flag, name, description):
    with Session(engine) as session:
        quality_flag = models.QualityFlag(satellite=satellite, flag=flag, name=name, description=description)
        session.add(quality_flag)
        session.commit()
        session.refresh(quality_flag)
    return quality_flag
