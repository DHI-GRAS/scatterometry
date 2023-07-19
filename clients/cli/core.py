import requests
import csv
import os
from datetime import timedelta
from pathlib import Path
import asyncio
import json
import aiohttp


def download_data(url, fn):
    print(f"DOWNLOADING")
    response = requests.get(url)
    if response.status_code == 200:
        with open(fn, "wb") as f:
            f.write(response.content)
        print(f"DOWNLOAD WAS SUCCESSFUL")
    else:
        print("DOWNLOAD WAS UNSUCCESSFUL")
        print(response.status_code)
        print(response.text)
        return


async def fetch(session, url, params, headers):
    async with session.get(url, params=params, headers=headers) as resp:
        return await resp.json()


async def fetch_urls(processes, urls):
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for u in processes:
            tasks.append(loop.create_task(fetch(session, u[0], u[1], u[2])))

        for result in asyncio.as_completed(tasks):
            response_text = await result
            if "status" not in response_text or response_text["status"] != "success":
                print(f"REQUEST WAS UNSUCCESSFUL: {u[1]}")
                print(response_text)
                continue
            else:
                print(f"REQUEST WAS SUCCESSFUL")
                urls.append(response_text["data"]["download_url"])
    return urls


def download_url(
    url,
    auth_headers,
    min_time,
    max_time,
    lat_max,
    lat_min,
    lon_max,
    lon_min,
    satellites,
    flags,
    time_steps,
):
    max_timestamp = min(min_time + timedelta(days=time_steps), max_time)
    print(f"REQUESTING TIME RANGE {min_time} to {max_timestamp}")
    params_all = {
        "timestamp_from": str(min_time),
        "timestamp_to": str(max_timestamp),
        "lat_max": lat_max,
        "lat_min": lat_min,
        "lon_max": lon_max,
        "lon_min": lon_min,
        "satellites": satellites,
        "flags": flags,
    }
    params = {key: value for key, value in params_all.items() if value is not None}

    return (url, params, auth_headers)


def get_header_row(file_path):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        header_row = next(reader)
    return header_row


def merge_csv_files(input_files, output_file):
    print("MERGING FILES")
    with open(output_file, "w", newline="") as outfile:
        writer = csv.writer(outfile)

        # Write the header row
        writer.writerow(get_header_row(input_files[0]))

        # Iterate over each input file
        for file_path in input_files:
            with open(file_path, "r") as infile:
                reader = csv.reader(infile)

                # Skip the header row in each input file
                next(reader)

                # Write the remaining rows to the output file
                for row in reader:
                    writer.writerow(row)
