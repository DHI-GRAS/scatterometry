import numpy as np
import pandas as pd
import re
import xarray as xr

from utils import BoundingBox, get_satellite_from_str


# file_path = "/data/lambis/Projects/Scatterometry/scatterometry/downloader/scatterometry-downloader/temp/rs_l2b_v2.0_climate_10600_201801282242.nc"


def parse_rapidscat(file_path, bbox: BoundingBox = None) -> pd.DataFrame:

    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        wind_speed = ds["retrieved_wind_speed"].values
        wind_direction = ds[
            "retrieved_wind_direction"
        ].values  # wind direction in degrees
        flags = ds["flags"].values
        # eflags = ds['eflags'].values
        lat = ds["lat"].values
        lon = ds["lon"].values
        time = ds["time"].values

    # reshape tiles to same shape as 2d variables
    time = np.tile(np.expand_dims(time, 1), (1, wind_speed.shape[1]))

    flag = (flags != 0).astype(int)

    # concatenate data for a dataframe
    df = pd.DataFrame(
        data={
            "lon": lon.flatten(),
            "lat": lat.flatten(),
            "timestamp": time.flatten(),
            "wind_speed": wind_speed.flatten(),
            "wind_direction": wind_direction.flatten(),
            "flag": flag.flatten(),
        }
    )

    # remove rows containing nan
    df = df.dropna()

    if bbox:
        df = df[
            df["lat"].between(bbox.lat_min, bbox.lat_max)
            & df["lon"].between(bbox.lon_min, bbox.lon_max)
        ]

    return df


def parse_cygnss(file_path, bbox: BoundingBox = None) -> pd.DataFrame:

    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        wind_speed = ds["wind_speed"].values
        fds_flag = ds["fds_sample_flags"].values
        lat = ds["sc_lat"].values
        lon = ds["sc_lon"].values
        time = ds["sample_time"].values

    flag = (fds_flag != 0).astype(int)

    df = pd.DataFrame(
        data={
            "lon": lon,
            "lat": lat,
            "timestamp": time,
            "wind_speed": wind_speed,
            "flag": flag,
        }
    )

    df = df.dropna()

    if bbox:
        df = df[
            df["lat"].between(bbox.lat_min, bbox.lat_max)
            & df["lon"].between(bbox.lon_min, bbox.lon_max)
        ]

    return df


def parse_oscat(file_path, bbox: BoundingBox = None) -> pd.DataFrame:

    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        wind_speed = ds["retrieved_wind_speed"].values
        wind_direction = ds[
            "retrieved_wind_direction"
        ].values  # wind direction in degrees
        flags = ds["flags"].values
        # eflags = ds['eflags'].values
        lat = ds["lat"].values
        lon = ds["lon"].values
        time = ds["time"].values

    # reshape tiles to same shape as 2d variables
    time = np.tile(np.expand_dims(time, 1), (1, wind_speed.shape[1]))

    flag = (flags != 124).astype(int)
    # concatenate data for a dataframe
    df = pd.DataFrame(
        data={
            "lon": lon.flatten(),
            "lat": lat.flatten(),
            "timestamp": time.flatten(),
            "wind_speed": wind_speed.flatten(),
            "wind_direction": wind_direction.flatten(),
            "flag": flag.flatten(),
        }
    )

    # remove rows containing nan in any column
    df = df.dropna()

    if bbox:
        df = df[
            df["lat"].between(bbox.lat_min, bbox.lat_max)
            & df["lon"].between(bbox.lon_min, bbox.lon_max)
        ]

    return df


def parse_quikscat(file_path, bbox: BoundingBox = None) -> pd.DataFrame:

    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        wind_speed = ds["retrieved_wind_speed"].values
        wind_direction = ds[
            "retrieved_wind_direction"
        ].values  # wind direction in degrees
        flags = ds["flags"].values
        eflags = ds["eflags"].values
        lat = ds["lat"].values
        lon = ds["lon"].values
        time = ds["time"].values

    # reshape tiles to same shape as 2d variables
    time = np.tile(np.expand_dims(time, 1), (1, wind_speed.shape[1]))

    flag = ((flags != 0) | (eflags != 1)).astype(int).astype(int)

    df = pd.DataFrame(
        data={
            "lon": lon.flatten(),
            "lat": lat.flatten(),
            "timestamp": time.flatten(),
            "wind_speed": wind_speed.flatten(),
            "wind_direction": wind_direction.flatten(),
            "flag": flag.flatten(),
        }
    )

    # remove rows containing nan in any column
    df = df.dropna()

    if bbox:
        df = df[
            df["lat"].between(bbox.lat_min, bbox.lat_max)
            & df["lon"].between(bbox.lon_min, bbox.lon_max)
        ]

    return df


def parse_ascatc(file_path, bbox: BoundingBox = None) -> pd.DataFrame:

    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        wind_speed = ds["wind_speed"].values
        wind_direction = ds[
            "wind_dir"
        ].values  # wind direction in degrees - with 0 degrees flowing north (oceanic convention)
        flags = ds["wvc_quality_flag"].values
        lat = ds["lat"].values
        lon = ds["lon"].values
        time = ds["time"].values

    flag = (flags.flatten() != 0).astype(int)

    df = pd.DataFrame(
        data={
            "lon": lon.flatten(),
            "lat": lat.flatten(),
            "timestamp": time.flatten(),
            "wind_speed": wind_speed.flatten(),
            "wind_direction": wind_direction.flatten(),
            "flag": flag,
        }
    )

    # remove rows containing nan in any column
    df = df.dropna()

    if bbox:
        df = df[
            df["lat"].between(bbox.lat_min, bbox.lat_max)
            & df["lon"].between(bbox.lon_min, bbox.lon_max)
        ]

    return df


def get_satellite_n_parser(filename):

    files_satellites_map = {
        "rscat": parse_rapidscat,
        "cygnss": parse_cygnss,
        "oscat": parse_oscat,
        "qscat": parse_quikscat,
        "ascat": parse_ascatc,
    }

    satellite_name = get_satellite_from_str(filename)

    return satellite_name, files_satellites_map[satellite_name]
