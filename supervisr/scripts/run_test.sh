#!/bin/bash -x
sudo python3 -m pip install -U -r ../requirements-dev.txt
git pull
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py test
coverage run --source='.' manage.py test
coverage report
isort -c -vb
pylint --load-plugins pylint_django supervisr*
prospector -I migration -I settings.py