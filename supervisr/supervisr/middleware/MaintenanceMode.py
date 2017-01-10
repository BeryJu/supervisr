from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import *

def maintenance_mode(get_response):
    setting, created = Setting.objects.get_or_create(
               key='supervisr:maintenancemode',
               defaults= {'value': 'False'})

    def middleware(req):
        if setting.value_bool is True:
            return render(req, 'common/maintenance.html')
        response = get_response(req)
        return response
    return middleware
