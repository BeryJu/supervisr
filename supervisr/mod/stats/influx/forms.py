"""Supervisr Mod Stats Influx Forms"""

from django import forms

from supervisr.core.forms.settings import SettingsForm


class InfluxSettingsForm(SettingsForm):
    """Settings Form"""

    namespace = 'supervisr.mod.stats.influx'
    settings = ['enabled', 'host', 'port', 'database', 'username', 'password']

    widgets = {
        'enabled': forms.BooleanField(required=False),
    }
