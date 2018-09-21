# Creating a module

## Setting up a development environment

Set up a new virtualenv with a least Python 3.5 and install the supervisr module.

```shell
virtualenv -p python3.5 env
source env/bin/activate
pip install -e git+https://git.beryju.org/BeryJu.org/supervisr.git#egg=supervisr[dev]
```

This will install all required dependencies.