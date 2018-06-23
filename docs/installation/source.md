# Installation directly from source

Supervisr is a python application which requires Python 3.5. To keep dependencies from clashing, we reccomend the usage of a virtualenv.

## Installation of OS dependencies

### Debian

`apt install python3.5 python3-pip python3-virtualenv git`

## Download supervisr

```bash
# Change to whatever folder you plan to install supervisr to
# cd /opt/
git clone https://git.beryju.org/BeryJu.org/supervisr.git
cp supervisr/local_settings_example.py supervisr/local_settings.py
# Adjust install settings, DB type, etc
vi supervisr/local_settings.py
```

## Installation of Python dependencies

### With virtualenv

```bash
virtualenv --python=python3.5 env
source env/bin/activate
pip install -U -r requirements.txt
```

### Without virtualenv

```bash
pip install -U -r requirements.txt
```

## Installing Database Migrations

```bash
python3 manage.py migrate
```

## Installing System Services and scripts

```bash
sudo cp debian/*.service /lib/systemd/system/
# Adjust the path to whatever path you installed supervisr in.
sudo vi /lib/systemd/system/supervisr*
sudo systemctl daemon-reload
sudo systemctl enable 'supervisr*'
sudo systemctl start 'supervisr*'
ln -s scripts/supervisr-ctl /usr/share/bin
```

## Initial Setup

```bash
# Create the initial admin user
supervisr-ctl utils.create_superuser
```

supervisr should now be listening on port 8000.
