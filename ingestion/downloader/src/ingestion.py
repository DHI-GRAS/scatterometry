import logging
import os

from os.path import join, basename
from subscriber import podaac_access as pa

import database

from df_formaters import format_df
from parsers import get_satellite_n_parser
from utils import BoundingBox


# data_path = "/data/lambis/Projects/Scatterometry/data-subscriber/rscat"
# file = "smth.smth"
# checksum = "asd10e1md021"


def handle_file(data_path, filename, url, checksum, bbox=None):

    logging.info(f"Parsing file {filename}")
    record_file = database.read_record_file(filename)

    if record_file and checksum == record_file.checksum:
        msg = f"File has already been parsed: {filename}"
        logging.info(msg)
        return

    if record_file:
        msg = f"Found updated version of file: {filename}. Updating its records"
        logging.info(msg)
        database.delete_records_of_file(record_file)
        database.delete_record_file(record_file)

    satellite_name, satellite_data_parser = get_satellite_n_parser(filename)
    filepath = join(data_path, basename(filename))
    if bbox:
        bbox = BoundingBox(bbox)

    pa.download_file(url, filepath)
    df = satellite_data_parser(filepath, bbox=bbox)
    record_file = database.create_record_file(filename=filename, checksum=checksum)
    satellite = database.read_satellite(satellite_name=satellite_name)
    df = format_df(df, record_file=record_file, satellite=satellite)
    database.write_records_from_data_frame(df)

    os.remove(filepath)
