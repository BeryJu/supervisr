"""
Supervisr Mod Namecheap Setup form
"""

from django import forms
from django.utils.translation import ugettext as _

from supervisr.core.forms.provider import NewCredentialDetailMeta
from supervisr.mod.namecheap.models import NamecheapCredentials


class SetupForm(forms.ModelForm):
    """
    Namecheap Provider Setup form
    """

    title = _('Namecheap API Information')

    class Meta(NewCredentialDetailMeta):

        model = NamecheapCredentials
        widgets = {
            'name': forms.TextInput(),
            'api_key': forms.TextInput(),
            'api_user': forms.TextInput(),
            'username': forms.TextInput(),
        }
