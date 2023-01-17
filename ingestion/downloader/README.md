# Ingestion

## Development
Prerequisites:
1. Create a `.netrc` in `$HOME` like the following. The file is needed to authenticate requests to earthdata.
    ```
    machine urs.earthdata.nasa.gov
        login <username>
        password <password>
    ```
2. Load the following environment variables as shown in `.env.example`
3. Install python modules requirements using the `requirements.txt`. In case the developer wants to upgrade the modules used, the `requirements_dev.txt` should be installed. The `requirements_dev.txt` holds the main modules used without their versions.

Run with:
```
cd ./src/download.py
python download.py
```

## Run
Run the image with:
```
docker run --rm \
    -e EARTHDATA_USERNAME=<username> \
    -e EARTHDATA_PASSWORD=<password> \
    -e DATABASE_URL="postgresql://<db-domain>/<db-name>?user=<user>&password=<password>" \
    scatterometry-downloader:v0.0.1  -c <sattelite collection ex. RSCAT_LEVEL_2B_OWV_CLIM_12_V2>
```
