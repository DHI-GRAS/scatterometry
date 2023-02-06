FROM python:3.11.1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install pip --upgrade \
    && pip install -r /app/requirements.txt

COPY ./src /app

CMD ["./entrypoint.sh"]
