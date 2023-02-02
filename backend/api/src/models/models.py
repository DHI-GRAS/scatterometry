from datetime import datetime
from geoalchemy2 import Geometry
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Column, Relationship
from typing import List, Optional, Any


# Models
class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str]

    satellites: List["Satellite"] = Relationship(back_populates="mission")


class Satellite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mission_id: int = Field(foreign_key="mission.id")
    mission: Mission = Relationship(back_populates="satellites")
    name: str
    is_active: bool = Field(default=True)
    description: Optional[str]
    wind_direction_correction_degrees: float = Field(default=0)

    versions: List["Version"] = Relationship(back_populates="satellite")
    quality_flags: List["QualityFlag"] = Relationship(back_populates="satellite")
    records: List["Record"] = Relationship(back_populates="satellite")

    __table_args__ = (
        UniqueConstraint("mission_id", "name", name="mission_id_name_uc"),
    )


class Version(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    satellite_id: int = Field(index=True, foreign_key="satellite.id")
    satellite: Satellite = Relationship(back_populates="versions")
    released_at: datetime

    records: List["Record"] = Relationship(back_populates="version")

    __table_args__ = (
        UniqueConstraint("satellite_id", "name", name="satellite_id_name_uc"),
    )


class QualityFlag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    satellite_id: int = Field(index=True, foreign_key="satellite.id")
    satellite: Satellite = Relationship(back_populates="quality_flags")
    flag: str = Field(index=True)
    name: str = Field(index=True)
    description: str = Field(default=None, nullable=True)

    records: List["Record"] = Relationship(back_populates="quality_flag")

    __table_args__ = (
        UniqueConstraint("satellite_id", "flag", name="satellite_id_flag_uc"),
    )


class RecordFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True, unique=True)
    checksum: str = Field(index=True)
    downloaded_at: datetime = Field(default=datetime.utcnow(), nullable=False)

    records: List["Record"] = Relationship(back_populates="record_file")


class Record(SQLModel, table=True):
    # Since this table is intended to be a timescale db hyper-table it can't have a primary key
    # ref: https://stackoverflow.com/a/61207247/9715816
    # Here many columns are assigned as candidate keys with `primary_key=True` and together they are identifying a unique item
    # Ref: https://docs.sqlalchemy.org/en/14/core/constraints.html
    # Later when the the table is converted to hyper-table timescale db will handle the features of primary keys
    point: Any = Field(
        sa_column=Column(Geometry("POINT")), index=True, primary_key=True
    )
    timestamp: datetime = Field(primary_key=True)
    wind_direction: Optional[float]
    wind_speed: Optional[float]
    quality_flag_id: int = Field(
        index=True, foreign_key="qualityflag.id", primary_key=True
    )
    quality_flag: QualityFlag = Relationship(back_populates="records")
    version_id: int = Field(
        index=True, foreign_key="version.id", default=None, nullable=True
    )
    version: Version = Relationship(back_populates="records")
    satellite_id: int = Field(index=True, foreign_key="satellite.id", primary_key=True)
    satellite: Satellite = Relationship(back_populates="records")
    record_file_id: int = Field(
        index=True, foreign_key="recordfile.id", primary_key=True
    )
    record_file: RecordFile = Relationship(back_populates="records")
