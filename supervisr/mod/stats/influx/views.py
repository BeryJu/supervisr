"""Supervisr Mod Influx Views"""
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext as _

from supervisr.core.views.settings import GenericSettingView
from supervisr.mod.stats.influx.forms import InfluxSettingsForm
from supervisr.mod.stats.influx.influx_client import InfluxClient


class SettingsView(GenericSettingView):
    """Influx Settings View"""

    template_name = 'stats/influx/settings.html'
    form = InfluxSettingsForm

    def post(self, request: HttpRequest) -> HttpResponse:
        if 'test' in request.POST:
            # Test button that sends a test message
            with InfluxClient() as client:
                client.write("test", value=128)
            messages.success(request, _('Successfully Sent test message'))
        return super().post(request)
