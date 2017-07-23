"""
Supervisr DNS DNSDomain Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class DNSDomainForm(forms.Form):
    """
    Create a new DNSdomain
    """

    title = 'General Information'
    domain = forms.ModelChoiceField(queryset=None, required=True,
                                    label=_('Domain'))
    provider = forms.ModelChoiceField(queryset=None, required=True,
                                      label=_('Provider'))
