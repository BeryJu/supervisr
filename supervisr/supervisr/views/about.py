from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render


def changelog(req):
    return render(req, 'about/changelog.html', {
        'changelog': settings.CHANGELOG
        })
