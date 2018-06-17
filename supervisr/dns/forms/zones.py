"""Supervisr DNS Zone Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from supervisr.dns.models import Zone


class ZoneForm(forms.ModelForm):
    """Create/edit ZoneForm"""

    title = _('General Information')

    class Meta:

        model = Zone
        fields = ['domain', 'providers', 'enabled']
