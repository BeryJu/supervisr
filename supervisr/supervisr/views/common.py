from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(req):
    return render(req, 'common/index.html')

def uncaught_404(req):
    return render(req, 'common/error.html', { 'code': 404 })

def uncaught_500(req):
    return render(req, 'common/error.html', { 'code': 500 })