"""
Supervisr DNS Record Forms
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.dns.models import Record


class RecordForm(forms.ModelForm):
    """
    Create/edit RecordForm
    """

    title = _('General Information')

    class Meta:

        model = Record
        fields = ['domain', 'name', 'type', 'content', 'ttl', 'prio', 'enabled']
