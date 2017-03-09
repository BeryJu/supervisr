"""
Supervisr Core Middleware to detect Maintenance Mode
"""

from django.shortcuts import render

from ..models import Setting


def maintenance_mode(get_response):
    """
    Middleware to detect Maintenance Mode
    """
    setting = Setting.objects.get_or_create(
        key='supervisr:maintenancemode',
        defaults={'value': 'False'})[0]

    def middleware(req):
        """
        Middleware to detect Maintenance Mode
        """
        if setting.value_bool is True:
            return render(req, 'common/maintenance.html')
        response = get_response(req)
        return response
    return middleware
