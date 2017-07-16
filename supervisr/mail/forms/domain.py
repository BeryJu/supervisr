"""
Supervisr Mail MailDomain Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class MailDomainForm(forms.Form):
    """
    Create a new maildomain
    """

    title = 'General Information'
    domain = forms.ModelChoiceField(queryset=None, required=True,
                                    label=_('Domain'))
    provider = forms.ModelChoiceField(queryset=None, required=True,
                                      label=_('Provider'))
    enabled = forms.BooleanField(required=False, initial=True, label=_('Enabled'))
