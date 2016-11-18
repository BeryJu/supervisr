#!/bin/bash -x
git pull
python manage.py makemigrations
python manage.py migrate
python manage.py runserver -v 3 0.0.0.0:8080
