import models

from datetime import datetime

from database import create_tables


# Add data
def add_test_data():

    mission = models.Mission(
        name="Mission Name",
    ).create()

    satellite = models.Satellite(
        mission_id=mission.id,
        name="Satellite Name",
        is_active=True,
    ).create()

    version = models.Version(
        name="Satellite Version",
        satellite_id=satellite.id,
        released_at=datetime(2021,10,10),
    ).create()

    quality_flag = models.QualityFlag(
        satellite_id=satellite.id,
        flag="1",
        description="A description about the flag",
    ).create()

    record_file = models.RecordFile(
        filename="my_data_file.nc",
        checksum="Ach3cksUm",
        downloaded_at=datetime(2022,12,31,17,12)
    ).create()


    r1 = models.Record(
        point="Point(20 0)",
        timestamp=datetime(2022,12,31,12,12),
        wind_direction=10,
        wind_speed=None,
        quality_flag_id=quality_flag.id,
        version_id=version.id,
        satellite_id=satellite.id,
        record_file_id=record_file.id
    ).create()
    # print(models.Mission.get(models.Mission.id == 1).read_related("satellites"))
    print(mission.read_related("satellites"))


if __name__ == "__main__":
    create_tables()
    add_test_data()
