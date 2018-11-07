FROM debian:buster-slim

LABEL Author="BeryJu.org <supervisr@beryju.org>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    SUPERVISR_ENV=docker

COPY . /supervisr/
RUN apt-get update && \
    apt-get install netcat build-essential python3 python3-pip python3-dev -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir setuptools && \
    python3 -m pip install --no-cache-dir -r /supervisr/requirements.txt && \
    apt-get remove --purge -y build-essential && \
    apt-get autoremove --purge -y
WORKDIR /supervisr/
