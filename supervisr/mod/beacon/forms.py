"""supervisr mod beacon settings forms"""

from django import forms

from supervisr.core.forms.settings import SettingsForm


class BeaconSettingsForm(SettingsForm):
    """Control beacon settings"""

    namespace = 'supervisr.mod.beacon'
    settings = ['enabled', 'endpoint']

    widgets = {
        'enabled': forms.BooleanField(required=False),
    }
