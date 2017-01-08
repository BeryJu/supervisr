from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import *

def maintenance_mode(get_response):
    mm_setting = Setting.objects.filter(pk='supervisr:MaintenanceMode')

    def middleware(req):
        if mm_setting.exists() is True and \
            mm_setting[0].value['enabled'] is True:
            return render(req, 'common/maintenance.html')
        response = get_response(req)
        return response
    return middleware
