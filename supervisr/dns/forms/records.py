"""
Supervisr DNS Record Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import Record


class RecordForm(forms.ModelForm):
    """
    Create/edit RecordForm
    """

    title = _('General Information')

    def clean_name(self):
        """Make sure name doesn't end with `.`"""
        name = self.cleaned_data.get('name')
        if name[-1] == '.':
            raise ValidationError(_('Name may not end with dot.'), code='invalid')
        return name

    # def clean_content(self):
    #     """Clean content based on selected type"""
    #     data = self.cleaned_data.get('content')
    #     type = self.cleaned_data.get('type')
    #     if type == 'A':
    #         validate_ipv4_address(data)
    #     elif type == 'AAAA':
    #         validate_ipv6_address(data)
    #     return data

    class Meta:

        model = Record
        fields = ['domain', 'name', 'enabled'] #'type', 'content', 'ttl', 'prio',
        # labels = {
        #     'prio': _('Priority'),
        #     'ttl': 'TTL',
        # }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Set to '@' for root-level records."}),
            # 'content': forms.TextInput(attrs={'placeholder': 'e.g. 1.2.3.4'}),
        }
