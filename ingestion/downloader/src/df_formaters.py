import database
import logging
import models
import geopandas as geopd


# satellite = database.read_satellite(satellite_name="rscat")
# record_file = database.read_record_file(filename="rs_l2b_v2.0_climate_10600_201801282242.nc")


def format_df(df, record_file: models.RecordFile, satellite: models.Satellite):
    """
    This function has crucial dependencies on the equivalent satellite parser
    """

    nullable_columns = ["version_id", "wind_direction", "wind_speed"]
    pk_subset = ["point", "timestamp", "quality_flag_id", "satellite_id", "record_file_id"]
    quality_flags = {quality_flag.flag: quality_flag.id for quality_flag in database.read_quality_flags(satellite_id=satellite.id)}

    for column in nullable_columns:
        if column not in df.columns:
            df[column] = None

    df["point"] = geopd.points_from_xy(df.lon, df.lat, crs="EPSG:4326")
    df["satellite_id"] = satellite.id
    df["record_file_id"] = record_file.id
    df["quality_flag_id"] = df["flag"].apply(lambda x: quality_flags[str(x)])

    df = df.drop(["lon", "lat", "flag"], axis=1)

    duplicates = df.duplicated(subset=pk_subset, keep=False)
    if duplicates.any():
        msg = (
            f"Found {duplicates.sum()} duplicate rows for columns combination "
            "point, timestamp, quality_flag_id, satellite_id, record_file_id.\n"
            "Dropping duplicates:\n",
            df[duplicates]
        )
        logging.warning(msg)
        df = df.drop_duplicates(subset=pk_subset, keep='last')

    return df
