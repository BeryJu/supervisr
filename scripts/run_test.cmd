@echo off
git pull
cd supervisr\
python manage.py makemigrations
python manage.py migrate
coverage run --source='.' manage.py test
isort -c -vb
pylint --load-plugins pylint_django supervisr supervisr_dns supervisr_mail supervisr_mod_ldap supervisr_server supervisr_web
prospector -I migration -I settings.py
cd ..
