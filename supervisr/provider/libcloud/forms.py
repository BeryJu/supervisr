"""supervisr mod libcloud provider forms"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.core.forms.providers import NewCredentialDetailMeta
from supervisr.provider.libcloud.models import LibCloudCredentials


class LibcloudCredentialForm(forms.ModelForm):
    """Form for basic input details"""

    title = 'libcloud Credentials'

    class Meta(NewCredentialDetailMeta):

        model = LibCloudCredentials
        labels = {
            'secret': _('Secret (optional)'),
            'host': _('Host (optional)'),
            'port': _('Port (optional)'),
            'api_version': _('API Version (optional)'),
            'region': _('Region (optional)')
        }
        widgets = {
            'name': forms.TextInput(),
            'key': forms.TextInput(),
            'secret': forms.TextInput(),
            'host': forms.TextInput(),
            'api_version': forms.TextInput(),
            'region': forms.TextInput(),
        }
