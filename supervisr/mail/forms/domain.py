"""
Supervisr Mail MailDomain Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.mail.models import MailDomain


class MailDomainForm(forms.ModelForm):
    """
    Create a new maildomain
    """

    title = 'General Information'

    class Meta:

        fields = ['domain', 'provider', 'destination', 'enabled']
        model = MailDomain
        widgets = {
            'destination': forms.TextInput(attrs={
                'placeholder': _("'internal' or DNS Name/IP to relay")}),
        }
