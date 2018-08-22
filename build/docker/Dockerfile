FROM python:3.6-slim-stretch

LABEL Author="BeryJu.org <supervisr@beryju.org>"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SUPERVISR_LOCAL_SETTINGS supervisr.local_settings_docker
ENV DOCKER_CONTAINER 1

RUN apt-get update && apt-get install netcat build-essential -y --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY . /supervisr/
RUN pip install --no-cache-dir -r /supervisr/requirements.txt && apt-get remove --purge -y build-essential && apt-get autoremove --purge -y
WORKDIR /supervisr/
