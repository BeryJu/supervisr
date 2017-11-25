"""
Supervisr Contrib Bacula filter Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.core.forms.settings import SettingsForm
from supervisr.mod.contrib.bacula.models import Client, Pool

LEVELS = (
    ('', _('---')),
    ('F', _('Full')),
    ('D', _('Delta')),
    ('I', _('Incremental')),
)

class BaculaSettingsForm(SettingsForm):
    """Bacula DB Settings"""

    namespace = 'supervisr.mod.contrib.bacula'
    settings = ['enabled', 'engine', 'name', 'user', 'password', 'host', 'port']

class JobFilterForm(forms.Form):
    """Form to filter jobs"""
    client = forms.ModelChoiceField(
        label=_('Client'), required=False, empty_label=_('---'), queryset=Client.objects.all())
    level = forms.ChoiceField(
        label=_('Level'), required=False, choices=LEVELS)
    pool = forms.ModelChoiceField(
        label=_('Pool'), required=False, empty_label=_('---'), queryset=Pool.objects.all())
