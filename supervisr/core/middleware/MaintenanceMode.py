"""Supervisr Core Middleware to detect Maintenance Mode"""

from django.shortcuts import render

from supervisr.core.models import Setting


def maintenance_mode(get_response):
    """Middleware to detect Maintenance Mode"""

    def middleware(request):
        """Middleware to detect Maintenance Mode"""

        setting = Setting.get_bool('maintenancemode', default=False)
        if setting is True and 'user' not in request and not request.user.is_superuser:
            return render(request, 'common/maintenance.html')
        response = get_response(request)
        return response
    return middleware
