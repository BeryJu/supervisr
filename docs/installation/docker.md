# Docker installation of supervisr

Since supervisr consists of multiple services, we recommend using docker-compose for this.

!!! warning
    The pre-built image is currently unable to install custom third-party extensions. For more information see [BeryJu.org/supervisr#735](https://git.beryju.org/BeryJu.org/supervisr/issues/735)

## Pre-built images

To run supervisr using pre-built images, use the docker-compose.yml file from [here](https://git.beryju.org/BeryJu.org/supervisr/raw/master/build/docker/docker-compose.prebuilt.yml). This will start a supervisr instance, one task runner instance, one task scheduler instance and one task monitor instance. The webinterface will be exposed on port `8000`

## Self-built images

If you want to build custom images with custom changes, you can use [this](https://git.beryju.org/BeryJu.org/supervisr/raw/master/build/docker/docker-compose.yml) docker-compose.yml file. This will build a new `beryjuorg/supervisr` image, and use it to run the supervisr stack.

### Changing MySQL credentials

To change the MySQL password, adjust it in `docker-compose.yml`...

```
[...]
      - MYSQL_DATABASE=supervisr
      - MYSQL_USER=supervisr
      - MYSQL_PASSWORD=<new password>
  redis:
    image: redis:latest
[...]
```

...and `supervisr/local_settings_docker.py`

```
[...]
        'NAME': 'supervisr',
        'USER': 'supervisr',
        'PASSWORD': '<new password>',
        'HOST': 'db',
        'PORT': '',
[...]
```
