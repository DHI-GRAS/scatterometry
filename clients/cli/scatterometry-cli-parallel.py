"""
A simple command line tool to interact with an API
"""

import click
import requests
import os
import pandas as pd
from datetime import timedelta
from multiprocessing import Process
from pathlib import Path
import shutil
import asyncio
import aiohttp
import core
import time

t0 = time.time()


API_URL = os.environ.get("API_URL", "https://scatterometry-api.azurewebsites.net")
API_RECORDS_ENDPOINT = "/records"
API_LIMITS_ENDPOINT = "/limits"
API_KEY = os.environ.get("API_KEY")


# A click command to connect to the records endpoint with the date time range parameter, max min longitude and latitude with default values, satellite name with default value none and flag name with default value  none
@click.command()
@click.option("--timestamp-from", default="2015-07-01T00:00:00")
@click.option("--timestamp-to", default="2016-07-01T00:00:00")
@click.option(
    "--lat-max", default="66.1673934471677825", help="Maximum latitude of the records"
)
@click.option(
    "--lat-min", default="47.5757028246874896", help="Minimum latitude of the records"
)
@click.option(
    "--lon-max", default="31.2326561543798604", help="Maximum longitude of the records"
)
@click.option(
    "--lon-min", default="-12.3983275886476694", help="Minimum longitude of the records"
)
@click.option("--satellites", default=None, help="Satellite name of the records")
@click.option("--flags", default=None, help="Flag name of the records")
@click.option(
    "--output-dir", default=r"../../Scatterometry", help="Flag name of the records"
)
@click.option(
    "--api-key", default=None, help="The API key to use for authentication"
)
def records(
    timestamp_from,
    timestamp_to,
    lat_max,
    lat_min,
    lon_max,
    lon_min,
    satellites,
    flags,
    output_dir,
    api_key,
):
    """
    Make a request to the records endpoint with all the non-empty parameters and add the authentication key in the header
    """

    # authorization key

    if not API_KEY and not api_key:
        print("ERROR: API_KEY environment variable not set nor --api-key argument was provided")
        return
    if API_KEY:
        api_key = API_KEY
    auth_headers = {"Authorization": api_key}

    # query the limits endpoint
    limits_url = API_URL + API_LIMITS_ENDPOINT
    response = requests.get(limits_url, headers=auth_headers)

    if response.status_code == 200:
        response_body = response.json()
    else:
        print("ERROR: limits request failed")
        print(response.status_code)
        print(response.text)
        return

    max_area = response_body["data"]["MAX_AREA_DEGREES"]
    max_hours = response_body["data"]["MAX_TIMESTAMP_DURATION_HOURS"]
    time_steps = int(max_hours / 24)

    # download the data
    url = API_URL + API_RECORDS_ENDPOINT

    # set the filename based on the request parameters, delete file if it already exists
    total_filename = f"records_{timestamp_from.replace(':', '')}_{timestamp_to.replace(':', '')}_{lat_max.replace('.', 'd')}_{lat_min.replace('.', 'd')}_{lon_max.replace('.', 'd')}_{lon_min.replace('.', 'd')}.csv"
    if os.path.exists(os.path.join(output_dir, total_filename)):
        os.remove(os.path.join(output_dir, total_filename))

    # temporary filename
    if os.path.exists(Path(output_dir) / "Temp"):
        shutil.rmtree(Path(output_dir) / "Temp")
    os.makedirs(Path(output_dir) / "Temp", exist_ok=False)

    # loop through the different days to download all the data
    time_range = pd.date_range(start=timestamp_from, end=timestamp_to, freq="D")

    urls = []
    processes = [
        core.download_url(
            url,
            auth_headers,
            time_range[i],
            time_range[-1],
            lat_max,
            lat_min,
            lon_max,
            lon_min,
            satellites,
            flags,
            time_steps,
        )
        for i in range(0, len(time_range) - 1, time_steps)
    ]

    asyncio.run(core.fetch_urls(processes, urls))
    temp_files = [
        os.path.join(Path(output_dir) / "Temp", f"file_{i}.csv")
        for i in range(len(urls))
    ]

    processes = [
        Process(target=core.download_data, args=(i, f))
        for i, f in zip(urls, temp_files)
    ]

    for process in processes:
        process.start()
    for process in processes:
        process.join()

    core.merge_csv_files(
        [
            os.path.join(Path(output_dir) / "Temp", i)
            for i in os.listdir(Path(output_dir) / "Temp")
        ],
        os.path.join(output_dir, total_filename),
    )

    shutil.rmtree(Path(output_dir) / "Temp")

    print("TOTAL REQUEST WAS SUCCESSFUL, FILE SAVED")
    print("Total time:", time.time() - t0)


if __name__ == "__main__":
    records()
