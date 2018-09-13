"""Supervisr DNS Record Forms"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import DataRecord, SetRecord


class SetRecordForm(forms.ModelForm):
    """Create/edit SetRecord"""

    title = _('General Information')

    def clean_name(self):
        """Make sure name doesn't end with `.`"""
        name = self.cleaned_data.get('name')
        if name[-1] == '.':
            raise ValidationError(_('Name may not end with dot.'), code='invalid')
        return name

    class Meta:

        model = SetRecord
        fields = ['name', 'enabled', 'append_name', 'records']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Set to '@' for root-level records."}),
        }
        help_texts = {
            'append_name': _('If true, names of records within this Set will be appended to '
                             'the parent. Otherwise all Records will be created with the name '
                             'of this Set.'),
        }


class DataRecordForm(forms.ModelForm):
    """Create/edit DataRecord"""

    title = _('General Information')

    def clean_name(self):
        """Make sure name doesn't end with `.`"""
        name = self.cleaned_data.get('name')
        if name[-1] == '.':
            raise ValidationError(_('Name may not end with dot.'), code='invalid')
        return name

    def clean_content(self):
        """Clean content based on selected type"""
        data = self.cleaned_data.get('content')
        _type = self.cleaned_data.get('type')
        if _type == 'A':
            validate_ipv4_address(data)
        elif _type == 'AAAA':
            validate_ipv6_address(data)
        return data

    class Meta:

        model = DataRecord
        fields = ['name', 'enabled', 'type', 'content', 'ttl', 'priority']
        labels = {
            'priority': _('Priority'),
            'ttl': 'TTL',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Set to '@' for root-level records."}),
            'content': forms.TextInput(attrs={'placeholder': 'e.g. 1.2.3.4'}),
        }
