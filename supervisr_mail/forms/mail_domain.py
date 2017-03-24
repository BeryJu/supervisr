"""
Supervisr Mail MailDomain Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class MailDomainForm(forms.Form):
    """
    Initial MailDomain Creation Form
    """
    title = _('General Information')

    domain = forms.ModelChoiceField(queryset=None, required=True,
                                    to_field_name='name', label=_('Domain'))
