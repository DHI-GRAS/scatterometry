#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from datetime import datetime
from os import makedirs
from os.path import isdir, basename, splitext
from urllib.error import HTTPError

from database import read_satellite, read_latest_satellite_record
from subscriber import podaac_access as pa
from ingestion import handle_file
from utils import get_satellite_from_str


page_size = 2000


def get_configuration():
    parser = create_parser()
    args = parser.parse_args()
    args.satellite_name = get_satellite_from_str(args.collection)

    if not args.startDate:
        satellite = read_satellite(args.satellite_name)
        latest_record = read_latest_satellite_record(satellite)
        args.startDate = latest_record.timestamp.strftime('%Y-%m-%dT%H:%M:%S') if latest_record else "1900-01-01"

    if not args.endDate:
        args.endDate = datetime.now().isoformat()

    return args


def prepare(args, token):

    # This cell will replace the timestamp above with the one read from the `.update` file in the data directory, if it exists.
    if not isdir(args.outputDirectory):
        logging.info("NOTE: Making new data directory at " + args.outputDirectory + "(This is the first run.)")
        makedirs(args.outputDirectory, exist_ok=True)

    temporal_range = pa.get_temporal_range(
        args.startDate,
        args.endDate,
        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    params = [
        ('page_size', page_size),
        ('sort_key', "-start_date"),
        ('provider', args.provider),
        ('ShortName', args.collection),
        ('temporal', temporal_range),
        ('token', token),
    ]

    if args.bbox is not None:
        params.append(('bounding_box', args.bbox))

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
            for  i, p in enumerate(params):
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
            if (related_url["Type"] == "EXTENDED METADATA") or ((related_url["Type"] == "GET DATA") and (('Subtype' not in related_url) or (related_url['Subtype'] != "OPENDAP DATA"))):
                if splitext(related_url['URL'])[-1] in pa.extensions:
                    urls.append((basename(related_url['URL']), related_url['URL']))

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
        raise Exception(f"There are residual items:\nurls: {urls}\nchecksums: {checksums}")

    return downloads


def create_parser():
    # Initialize parser
    parser = argparse.ArgumentParser(prog='PO.DAAC bulk-data downloader')

    # Adding Required arguments
    parser.add_argument("-c", "--collection-shortname", dest="collection", required=True,
                        help="The collection shortname for which you want to retrieve data.")  # noqa E501
    parser.add_argument("-d", "--data-dir", dest="outputDirectory", required=False, default="./temp",
                        help="The directory where data products will be downloaded.")  # noqa E501

    # Required through validation
    parser.add_argument("--cycle", required=False, dest="search_cycles",
                        help="Cycle number for determining downloads. can be repeated for multiple cycles",
                        action='append', type=int)
    parser.add_argument("-sd", "--start-date", required=False, dest="startDate",
                        help="The ISO date time after which data should be retrieved. For Example, --start-date 2021-01-14T00:00:00Z")  # noqa E501
    parser.add_argument("-ed", "--end-date", required=False, dest="endDate",
                        help="The ISO date time before which data should be retrieved. For Example, --end-date 2021-01-14T00:00:00Z")  # noqa E501

    # Adding optional arguments
    parser.add_argument("-f", "--force", dest="force", action="store_true", help = "Flag to force downloading files that are listed in CMR query, even if the file exists and checksum matches")  # noqa E501

    # spatiotemporal arguments
    parser.add_argument("-b", "--bounds", dest="bbox",
                        help="The bounding rectangle to filter result in. Format is W Longitude,S Latitude,E Longitude,N Latitude without spaces. Due to an issue with parsing arguments, to use this command, please use the -b=\"-180,-90,180,90\" syntax when calling from the command line. Default: \"-180,-90,180,90\".",
                        default=None)  # noqa E501

    # Arguments for how data are stored locally - much processing is based on
    # the underlying directory structure (e.g. year/Day-of-year)
    parser.add_argument("-dc", dest="cycle", action="store_true",
                        help="Flag to use cycle number for directory where data products will be downloaded.")  # noqa E501
    parser.add_argument("-dydoy", dest="dydoy", action="store_true",
                        help="Flag to use start time (Year/DOY) of downloaded data for directory where data products will be downloaded.")  # noqa E501
    parser.add_argument("-dymd", dest="dymd", action="store_true",
                        help="Flag to use start time (Year/Month/Day) of downloaded data for directory where data products will be downloaded.")  # noqa E501
    parser.add_argument("-dy", dest="dy", action="store_true",
                        help="Flag to use start time (Year) of downloaded data for directory where data products will be downloaded.")  # noqa E501
    parser.add_argument("--offset", dest="offset",
                        help="Flag used to shift timestamp. Units are in hours, e.g. 10 or -10.")  # noqa E501

    parser.add_argument("-e", "--extensions", dest="extensions",
                        help="The extensions of products to download. Default is [.nc, .h5, .zip, .tar.gz]",
                        default=None, action='append')  # noqa E501

   # Get specific granule from the search
   # https://github.com/podaac/data-subscriber/issues/109
    parser.add_argument("-gr", "--granule-name", dest="granulename",
                        help="Flag to download specific granule from a collection. This parameter can only be used if you know the granule name. Only one granule name can be supplied",
                        default=None)

    parser.add_argument("--process", dest="process_cmd",
                        help="Processing command to run on each downloaded file (e.g., compression). Can be specified multiple times.",
                        action='append')

    parser.add_argument("--verbose", dest="verbose", action="store_true", help="Verbose mode.")  # noqa E501
    parser.add_argument("-p", "--provider", dest="provider", default='POCLOUD',
                        help="Specify a provider for collection search. Default is POCLOUD.")  # noqa E501

    parser.add_argument("--limit", dest="limit", default=None, type=int,
                        help="Integer limit for number of granules to download. Useful in testing. Defaults to no limit.")  # noqa E501

    return parser


def run():

    args = get_configuration()

    logging.info(f"Ingesting data for satellite {args.satellite_name} from {args.startDate} to {args.endDate}")

    pa.setup_earthdata_login_auth(pa.edl)
    token = pa.get_token(pa.token_url)

    params = prepare(args, token)
    results = get_results(params, args, token)
    downloads = get_files_to_download(results)

    logging.info("Found " + str(len(downloads)) + " total files to download")

    for filename, url, checksum in downloads:
        try:
            handle_file(args.outputDirectory, filename, url, checksum, bbox=args.bbox)
        except Exception:
            logging.warning(str(datetime.now()) + " FAILURE: " + url, exc_info=True)

    logging.info("END\n\n")


def main():
    log_level = os.environ.get('PODAAC_LOGLEVEL', 'INFO').upper()
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                        level=log_level)
    logging.debug("Log level set to " + log_level)

    try:
        run()
    except Exception as e:
        logging.exception("Uncaught exception occurred during execution.")
        exit(hash(e))

if __name__ == '__main__':
    main()
