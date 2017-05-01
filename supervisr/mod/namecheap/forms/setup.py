"""
Supervisr Mod Namecheap Setup form
"""

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _


class SetupForm(forms.Form):
    """
    Namecheap Provider Setup form
    """

    title = _('Namecheap API Information')

    # Fields
    api_key = forms.CharField()
    api_username = forms.CharField()
    username = forms.CharField()
    sandbox = forms.BooleanField(initial=settings.DEBUG)