@echo off
git pull
python manage.py makemigrations supervisr
python manage.py migrate
python manage.py runserver
