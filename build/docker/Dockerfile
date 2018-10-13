FROM python:3.6-slim-stretch

LABEL Author="BeryJu.org <supervisr@beryju.org>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    SUPERVISR_ENV=docker

COPY . /supervisr/
RUN apt-get update && \
    apt-get install netcat build-essential -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r /supervisr/requirements.txt && \
    apt-get remove --purge -y build-essential && \
    apt-get autoremove --purge -y
WORKDIR /supervisr/
