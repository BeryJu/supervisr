"""
Supervisr Mod Auth SAML IDP Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from supervisr.core.forms.settings import SettingsForm


class IDPSettingsForm(SettingsForm):
    """IDP Settings Form"""

    namespace = 'supervisr.mod.auth.saml.idp'
    settings = ['issuer', 'signing', 'certificate', 'private_key', 'assertion_valid_for']

    widgets = {
        'signing': forms.BooleanField(label=_('Signing'), initial=True, required=False),
        'certificate': forms.CharField(label=_('Certificate'), widget=forms.Textarea()),
        'private_key': forms.CharField(label=_('Private Key'), widget=forms.Textarea()),
        'assertion_valid_for': forms.IntegerField(label=('Assertions are valid for (in minutes)')),
    }
