FROM python:3.11.1

WORKDIR /scatterometry-downloader

COPY ./requirements.txt /scatterometry-downloader/requirements.txt

RUN pip install pip --upgrade \
    && pip install -r requirements.txt

COPY ./src /scatterometry-downloader

ENTRYPOINT  ["./entrypoint.sh"]
