#!/bin/bash -x

which python3 2> /dev/null
if [ $? -eq 0 ]; then
    PY=$(which python3)
else
    PY=$(which python)
fi
echo "Running with python executable $PY"
sudo pip3 install -U -r requirements-dev.txt
git pull
cd supervisr/
"$PY" manage.py makemigrations
"$PY" manage.py migrate
"$PY" manage.py test
coverage run --source='.' manage.py test
coverage report
isort -c -vb
pylint --load-plugins pylint_django supervisr*
prospector -I migration -I settings.py