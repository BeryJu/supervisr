#!/bin/bash -x
find . | grep .pyc$ | xargs rm
sudo pip install -U -r ../requirements.txt
git pull
python manage.py makemigrations
python manage.py migrate
python manage.py runserver -v 3 0.0.0.0:8080