@echo off
python manage.py makemigrations
python manage.py migrate
coverage run --source='.' manage.py test
isort -c -vb
pylint --load-plugins pylint_django supervisr
prospector -I migration -I settings.py