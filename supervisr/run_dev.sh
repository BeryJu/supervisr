#!/bin/bash -x
find . | grep .pyc$ | xargs rm
sudo python3 -m pip install -U -r ../requirements.txt
git pull
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8080
