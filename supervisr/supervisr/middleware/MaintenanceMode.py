from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import *

class MaintenanceMode(object):

    def process_request(self, req):
        mm_setting = Setting.objects.get('supervisr:MaintenanceMode')
        if mm_setting.value['enabled'] is True:
            return render(req, 'common/maintenance.html')
        else:
            return None