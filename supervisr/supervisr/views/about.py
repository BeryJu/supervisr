from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

def changelog(req):
    return render(req, 'about/changelog.html', {
        'changelog': settings.CHANGELOG
        })