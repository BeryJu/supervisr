"""
Supervisr Mod Auth SAML IDP Forms
"""

from django import forms
from django.utils.translation import ugettext_lazy as _


class SettingsForm(forms.Form):
    """
    Settings Form
    """

    issuer = forms.CharField(label=_('Issuer'))
    signing = forms.BooleanField(label=_('Signing'), initial=True, required=False)
    certificate = forms.CharField(label=_('Certificate'), widget=forms.Textarea())
    private_key = forms.CharField(label=_('Private Key'), widget=forms.Textarea())
