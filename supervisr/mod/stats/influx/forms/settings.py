"""
Supervisr Mod Stats Influx Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class SettingsForm(forms.Form):
    """
    Settings Form
    """

    enabled = forms.BooleanField(label=_('Enabled'), initial=False, required=False)
    host = forms.CharField(label=_('Hostname'),
                           widget=forms.TextInput(attrs={
                               'placeholder': 'influx1.corp.exmaple.com'}))
    port = forms.IntegerField(label=_('Port'), initial=8086, max_value=65535, min_value=0,
                              widget=forms.TextInput(attrs={'placeholder': 8086}))
    database = forms.CharField(label=_('Database'), initial='supervisr')
    username = forms.CharField(label=_('User'), initial='root')
    password = forms.CharField(label=_('Password'), initial='root')
