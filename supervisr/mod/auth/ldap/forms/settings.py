"""
Supervisr Mod LDAP Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class SettingsForm(forms.Form):
    """
    Settings form
    """

    order = ['enabled', 'host', 'base', 'create_base', 'bind_user', 'bind_password', 'domain']
    enabled = forms.BooleanField(label=_('Enabled'), initial=False, required=False)
    host = forms.CharField(label=_('Hostname'),
                           widget=forms.TextInput(
                               attrs={'placeholder': 'dc1.corp.exmaple.com'}))
    base = forms.CharField(label=_('Base DN'),
                           widget=forms.TextInput(
                               attrs={'placeholder': 'DC=corp,DC=exmaple,DC=com'}))
    create_base = forms.CharField(label=_('Create Base DN'),
                                  widget=forms.TextInput(
                                      attrs={'placeholder': 'DC=corp,DC=exmaple,DC=com'}))
    bind_user = forms.CharField(label=_('Bind User'),
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Administrator'}))
    bind_password = forms.CharField(label=_('Bind Password'))
    domain = forms.CharField(label=_('Domain'),
                             widget=forms.TextInput(
                                 attrs={'placeholder': 'corp.example.com'}))
