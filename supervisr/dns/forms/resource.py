"""
Supervisr DNS ResourceSet Forms
"""

from django import forms
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import Resource


class ResourceForm(forms.ModelForm):
    """Create/edit ResourceSetForm"""

    title = _('General Information')

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

        model = Resource
        fields = ['name', 'enabled', 'type', 'content', 'ttl', 'priority']
        labels = {
            'priority': _('Priority'),
            'ttl': 'TTL',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ("Descriptive name. "
                                                           "This name is just used "
                                                           "within supervisr.")}),
            'content': forms.TextInput(attrs={'placeholder': 'e.g. 1.2.3.4'}),
        }
