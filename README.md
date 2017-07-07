# supervisr

![icon](assets/img/icon.png)

[![build status](https://git.beryju.org/BeryJu.org/supervisr/badges/master/build.svg)](https://git.beryju.org/BeryJu.org/supervisr/commits/master)
[![coverage report](https://git.beryju.org/BeryJu.org/supervisr/badges/master/coverage.svg)](https://git.beryju.org/BeryJu.org/supervisr/commits/master)


## Create a superuser by CLI

```
python .\manage.py createsuperuser
python .\manage.py shell
from supervisr.core.models import UserProfile
from django.contrib.auth.models import User
a = User.objects.all()[2]
a.is_staff = True
a.is_superuser = True
a.is_active = True
a.save()
UserProfile.objects.create(user=a)
```
