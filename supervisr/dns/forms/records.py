"""
Supervisr DNS Record Forms
"""

from django import forms
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import Record


class RecordForm(forms.ModelForm):
    """
    Create/edit RecordForm
    """

    title = _('General Information')

    def clean_content(self):
        """
        Clean content based on selected type
        """
        data = self.cleaned_data['content']
        type = self.cleaned_data['type']
        if type == 'A':
            validate_ipv4_address(data)
        elif type == 'AAAA':
            validate_ipv6_address(data)
        return data

    class Meta:

        model = Record
        fields = ['domain', 'name', 'type', 'content', 'ttl', 'prio', 'enabled']
        labels = {
            'prio': _('Priority'),
            'ttl': 'TTL',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Set to '@' for root-level records."}),
            'content': forms.TextInput(attrs={'placeholder': 'e.g. 1.2.3.4'}),
        }
