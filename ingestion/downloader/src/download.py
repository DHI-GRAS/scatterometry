#!/usr/bin/env python3
import click
import argparse
import logging
import os
import sys
from datetime import datetime
from os import makedirs
from os.path import isdir, basename, splitext
from urllib.error import HTTPError

from database import (
    read_satellite,
    read_latest_satellite_record,
    read_earliest_satellite_record,
)
from subscriber import podaac_access as pa
from ingestion import handle_file
from utils import get_satellite_from_str


page_size = 2000


def get_configuration(
    mode,
    collection,
    output_directory,
    start_date,
    end_date,
    bbox,
    verbose,
    provider,
):

    configurations_func_map = {
        "get": get_mode_configuration,
        "update": update_mode_configuration,
    }

    args = argparse.Namespace(
        collection=collection,
        output_directory=output_directory,
        start_date=start_date,
        end_date=end_date,
        bbox=bbox,
        verbose=verbose,
        provider=provider,
    )

    args.satellite_name = get_satellite_from_str(args.collection)

    return configurations_func_map[mode](args)


def get_mode_configuration(args):

    if not args.start_date:
        satellite = read_satellite(args.satellite_name)
        latest_record = read_latest_satellite_record(satellite)
        args.start_date = (
            latest_record.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
            if latest_record
            else "1900-01-01"
        )

    if not args.end_date:
        args.end_date = datetime.now().isoformat()

    return args


def update_mode_configuration(args):

    if not args.start_date or not args.end_date:
        satellite = read_satellite(args.satellite_name)

    if not args.start_date:
        earliest_record = read_earliest_satellite_record(satellite)
        args.start_date = earliest_record.timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    if not args.end_date:
        latest_record = read_latest_satellite_record(satellite)
        args.end_date = latest_record.timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    return args


def prepare(args, token):

    # This cell will replace the timestamp above with the one read from the `.update` file in the data directory, if it exists.
    if not isdir(args.output_directory):
        logging.info(
            "NOTE: Making new data directory at "
            + args.output_directory
            + "(This is the first run.)"
        )
        makedirs(args.output_directory, exist_ok=True)

    temporal_range = pa.get_temporal_range(
        args.start_date, args.end_date, datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    params = [
        ("page_size", page_size),
        ("sort_key", "-start_date"),
        ("provider", args.provider),
        ("ShortName", args.collection),
        ("temporal", temporal_range),
        ("token", token),
    ]

    if args.bbox is not None:
        params.append(("bounding_box", args.bbox))

    return params


def get_results(params, args, token):

    # If 401 is raised, refresh token and try one more time
    for _ in range(2):
        try:
            results = pa.get_search_results(params, args.verbose)
            break
        except HTTPError as e:
            if e.code != 401:
                raise e
            token = pa.refresh_token(token)
            for i, p in enumerate(params):
                if p[1] == "token":
                    params[i] = ("token", token)
    else:
        raise Exception("Could not get search results")

    return results


def get_files_to_download(results):
    urls = []
    checksums = {}
    for item in results["items"]:

        for related_url in item["umm"]["RelatedUrls"]:
            if (related_url["Type"] == "EXTENDED METADATA") or (
                (related_url["Type"] == "GET DATA")
                and (
                    ("Subtype" not in related_url)
                    or (related_url["Subtype"] != "OPENDAP DATA")
                )
            ):
                if splitext(related_url["URL"])[-1] in pa.extensions:
                    urls.append((basename(related_url["URL"]), related_url["URL"]))

        for granule in item["umm"]["DataGranule"]["ArchiveAndDistributionInformation"]:
            if splitext(granule["Name"])[-1] in pa.extensions:
                checksums[granule["Name"]] = granule["Checksum"]["Value"]

    downloads = []
    for i in reversed(range(len(urls))):
        filename, url = urls[i]
        if filename in checksums:
            downloads.append((filename, url, checksums[filename]))
            urls.pop(i)
            del checksums[filename]

    if len(urls) != 0 or len(checksums) != 0:
        raise Exception(
            f"There are residual items:\nurls: {urls}\nchecksums: {checksums}"
        )

    return downloads


def run(args):

    logging.info(
        f"Ingesting data for satellite {args.satellite_name} from {args.start_date} to {args.end_date}"
    )

    pa.setup_earthdata_login_auth(pa.edl)
    token = pa.get_token(pa.token_url)

    params = prepare(args, token)
    results = get_results(params, args, token)
    downloads = get_files_to_download(results)

    logging.info("Found " + str(len(downloads)) + " total files to download")

    for filename, url, checksum in downloads:
        try:
            handle_file(args.output_directory, filename, url, checksum, bbox=args.bbox)
        except Exception:
            logging.warning(str(datetime.now()) + " FAILURE: " + url, exc_info=True)

    logging.info("END\n\n")


@click.command()
@click.option(
    "--mode",
    "mode",
    required=True,
    default="get",
    help="The downloading-ingestion mode. Options are: get, update. In get mode only new data are ingested. In update mode the existing data get updated.",
)
@click.option(
    "-c",
    "--collections-shortnames",
    "collections",
    required=True,
    help="A list of collections shortnames for which you want to retrieve data.",
)
@click.option(
    "-d",
    "--data-dir",
    "output_directory",
    required=False,
    default="./temp",
    help="The directory where data products will be downloaded.",
)
@click.option(
    "-sd",
    "--start-date",
    "start_date",
    required=False,
    help="The ISO date time after which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z",
)
@click.option(
    "-ed",
    "--end-date",
    "end_date",
    required=False,
    help="The ISO date time before which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z",
)
@click.option(
    "-b",
    "--bounds",
    "bbox",
    default=None,
    help='The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b="-180,-90,180,90" syntax when calling from the command line. Default: "-180,-90,180,90".',
)
@click.option("--verbose", "verbose", is_flag=True, help="Verbose mode.")
@click.option(
    "-p",
    "--provider",
    "provider",
    default="POCLOUD",
    help="Specify a provider for collection search. Default is POCLOUD.",
)
def main(
    mode,
    collections,
    output_directory,
    start_date,
    end_date,
    bbox,
    verbose,
    provider,
):
    log_level = os.environ.get("PODAAC_LOGLEVEL", "INFO").upper()
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        level=log_level,
    )
    logging.debug("Log level set to " + log_level)

    for collection in collections.split(","):
        try:
            args = get_configuration(
                mode,
                collection,
                output_directory=output_directory,
                start_date=start_date,
                end_date=end_date,
                bbox=bbox,
                verbose=verbose,
                provider=provider,
            )
            run(args)
        except Exception as e:
            logging.exception("Uncaught exception occurred during execution.")


if __name__ == "__main__":
    main()
