from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def changelog(req):
    return render(req, 'about/changelog.html')