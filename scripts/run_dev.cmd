@echo off
git pull
cd supervisr\
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
