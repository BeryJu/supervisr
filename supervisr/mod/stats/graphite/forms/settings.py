"""
Supervisr Mod Stats Graphite Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class SettingsForm(forms.Form):
    """
    Settings Form
    """

    order = ['enabled', 'host', 'port', 'prefix']
    enabled = forms.BooleanField(label=_('Enabled'), initial=False, required=False)
    host = forms.CharField(label=_('Hostname'),
                           widget=forms.TextInput(attrs={
                               'placeholder': 'graphite1.corp.exmaple.com'}))
    port = forms.IntegerField(label=_('Port'), initial=2003, max_value=65535, min_value=0,
                              widget=forms.TextInput(attrs={'placeholder': 2003}))
    prefix = forms.CharField(label=_('Prefix'), initial='supervisr')
