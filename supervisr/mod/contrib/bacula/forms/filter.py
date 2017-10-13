"""
Supervisr Contrib Bacula filter Forms
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.mod.contrib.bacula.models import Client, Pool

LEVELS = (
    ('', _('---')),
    ('F', _('Full')),
    ('D', _('Delta')),
    ('I', _('Incremental')),
)

class JobFilterForm(forms.Form):
    """
    Form to filter jobs
    """
    client = forms.ModelChoiceField(
        label=_('Client'), required=False, empty_label=_('---'), queryset=Client.objects.all())
    level = forms.ChoiceField(
        label=_('Level'), required=False, choices=LEVELS)
    pool = forms.ModelChoiceField(
        label=_('Pool'), required=False, empty_label=_('---'), queryset=Pool.objects.all())
