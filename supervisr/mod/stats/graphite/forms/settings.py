
from django import forms
from django.utils.translation import ugettext as _

from supervisr.core.forms.core import InlineForm


class SettingsForm(InlineForm):

    order = ['enabled', 'host', 'port', 'prefix']
    enabled = forms.BooleanField(label=_('Enabled'), initial=False, required=False)
    host = forms.CharField(label=_('Hostname'))
    port = forms.IntegerField(label=_('Port'), initial=2003, max_value=65535, min_value=0)
    prefix = forms.CharField(label=_('Prefix'), initial='supervisr')
