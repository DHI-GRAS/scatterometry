"""
A simple command line tool to interact with an API
"""

import click
import requests
import json
import os
import pandas as pd
from datetime import timedelta


API_URL = os.environ.get("API_URL", "https://scatterometry-api.azurewebsites.net")
API_RECORDS_ENDPOINT = "/records"
API_KEY = os.environ.get("API_KEY")
print(API_KEY)


# A click command to connect to the records endpoint with the date time range parameter, max min longitude and latitude with default values, satellite name with default value none and flag name with default value  none
@click.command()
@click.option("--timestamp-from", default="2015-07-01T00:00:00")
@click.option("--timestamp-to", default="2015-12-03T00:00:00")
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
    Make a request to the records endpoint with the all the non-empty parameters and add the authentication key in the header
    """
    url = API_URL + API_RECORDS_ENDPOINT

    # set the filename based on the request parameters, delete file if it already exists
    filename = f"records_{timestamp_from.replace(':', '')}_{timestamp_to.replace(':', '')}_{lat_max.replace('.', 'd')}_{lat_min.replace('.', 'd')}_{lon_max.replace('.', 'd')}_{lon_min.replace('.', 'd')}.csv"
    if os.path.exists(os.path.join(output_dir, filename)):
        os.remove(os.path.join(output_dir, filename))

    # authorization key
    if not API_KEY and not api_key:
        print("ERROR: API_KEY environment variable not set nor --api-key argument was provided")
        return
    if API_KEY:
        api_key = API_KEY
    auth_headers = {"Authorization": api_key}
    # loop through the different days to download all the data
    time_range = pd.date_range(start=timestamp_from, end=timestamp_to, freq="D")

    for i in range(0, len(time_range) - 1, 31):
        max_timestamp = min(time_range[i] + timedelta(days=31), time_range[-1])
        print(f"DOWNLOADING TIME RANGE {time_range[i]} to {max_timestamp}")
        params_all = {
            "timestamp_from": time_range[i],
            "timestamp_to": max_timestamp,
            "lat_max": lat_max,
            "lat_min": lat_min,
            "lon_max": lon_max,
            "lon_min": lon_min,
            "satellites": satellites,
            "flags": flags,
        }
        params = {key: value for key, value in params_all.items() if value is not None}

        response = requests.get(url, params=params, headers=auth_headers)
        if response.status_code == 200:
            response_body = response.json()
            print(response_body)
            print(
                f"REQUEST FOR TIME RANGE {time_range[i]} - {max_timestamp} WAS SUCCESSFUL"
            )
        else:
            print(
                f"REQUEST FOR TIME RANGE {time_range[i]} - {max_timestamp} WAS UNSUCCESSFUL"
            )
            print(response.status_code)
            print(response.text)
            return

        # The response contains a url pointing to a file. Download that file
        url_ = response_body["data"]["download_url"]
        response = requests.get(url_)

        if response.status_code == 200:
            if i == 0:
                # write first file with header
                with open(os.path.join(output_dir, filename), "wb+") as f:
                    f.write(response.content)
            else:
                # remove header for all following files
                with open(os.path.join(output_dir, filename), "ab+") as f:
                    index = response.content.find(b"\nrscat,") + len("\nrscat,")
                    f.write(response.content[index:])
            print(f"TIME RANGE {time_range[i]} - {max_timestamp} ADDED TO FILE")
        else:
            print("REQUEST WAS UNSUCCESSFUL")
            print(response.status_code)
            print(response.text)
            return
    print("TOTAL REQUEST WAS SUCCESSFUL, FILE SAVED")


if __name__ == "__main__":
    records()
