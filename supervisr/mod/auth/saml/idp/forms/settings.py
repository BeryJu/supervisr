"""
Supervisr Mod Auth SAML IDP Forms
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.core.forms.core import InlineForm


class SettingsForm(InlineForm):
    """
    Settings Form
    """

    order = ['issuer', 'signing', 'autosubmit', 'certificate', 'private_key']
    issuer = forms.CharField(label=_('Issuer'))
    signing = forms.BooleanField(label=_('Signing'), initial=True, required=False)
    autosubmit = forms.BooleanField(label=_('Auto-Submit'), initial=True, required=False)
    certificate = forms.CharField(label=_('Certificate'), widget=forms.Textarea())
    private_key = forms.CharField(label=_('Private Key'), widget=forms.Textarea())
