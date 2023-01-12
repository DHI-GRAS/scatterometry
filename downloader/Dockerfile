FROM python:3.11.1-slim-buster

COPY ./scatterometry-downloader /scatterometry-downloader

WORKDIR /scatterometry-downloader

RUN pip install pip --upgrade \
    && pip install -r requirements.txt

CMD ./entrypoint.sh
