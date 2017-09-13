"""
Supervisr Core Provider Forms
"""

import logging

from django import forms
from django.forms import ModelForm
from django.http import Http404
from django.utils.translation import ugettext as _

from supervisr.core.models import (APIKeyCredential, ProviderInstance,
                                   UserPasswordCredential,
                                   UserPasswordServerCredential)
from supervisr.core.providers.base import get_providers
from supervisr.core.providers.internal import InternalCredential
from supervisr.core.utils import path_to_class

LOGGER = logging.getLogger(__name__)

class ProviderForm(ModelForm):
    """
    Form create/edit a new Provider
    """

    title = 'General Information'

    name = forms.CharField(required=True, label=_('Instance Name'))
    provider_path = forms.ChoiceField(choices=[], required=True, label=_('Provider'))
    credentials = forms.ModelChoiceField(queryset=None, required=True, label=_('Credentials'))

    def clean_credentials(self):
        """
        Import Provider and check if credentials are compatible
        """
        # Import provider based on form
        valid_providers = get_providers(path=True)
        if self.cleaned_data.get('provider_path') not in valid_providers:
            raise Http404
        # also check in form if class exists and is subclass of BaseProvider
        _class = path_to_class(self.cleaned_data.get('provider_path'))
        # Get credentials
        if self.cleaned_data.get('credentials').owner != self.request.user:
            raise Http404
        r_creds = self.cleaned_data.get('credentials').cast()
        # Check if credentials work with provider
        prov_inst = _class(r_creds)
        LOGGER.info("About to provider.check_credentials")
        prov_inst.check_credentials(r_creds)
        return self.cleaned_data.get('credentials')

    class Meta:

        model = ProviderInstance
        fields = ['name', 'provider_path', 'credentials']

class CredentialForm(forms.Form):
    """
    Form create/edit a new Credential
    """

    title = 'General Information'

    credential_type = forms.ChoiceField(choices=[], required=True,
                                        label=_('Credential Type'))

#pylint: disable=too-few-public-methods
class NewCredentialDetailMeta:
    """
    Base Class for Credentials Form Meta
    """

    exclude = ['owner']
    widgets = {
        'name': forms.TextInput(),
    }

class InternalCredentialForm(ModelForm):
    """
    Form for basic input details
    """

    title = 'Internal Credentials'

    class Meta(NewCredentialDetailMeta):

        model = InternalCredential

class NewCredentialAPIForm(ModelForm):
    """
    Form to input credential details
    """
    title = 'API Credentials'

    class Meta(NewCredentialDetailMeta):

        model = APIKeyCredential
        widgets = {
            'name': forms.TextInput(),
            'api_key': forms.TextInput(),
        }

class NewCredentialUserPasswordForm(ModelForm):
    """
    For to input credential details
    """
    title = 'User and Password'

    class Meta(NewCredentialDetailMeta):

        model = UserPasswordCredential
        widgets = {
            'name': forms.TextInput(),
            'username': forms.TextInput(),
            'password': forms.TextInput(),
        }

class NewCredentialUserPasswordServerForm(ModelForm):
    """
    For to input credential details
    """
    title = 'User, Password and Server'

    class Meta(NewCredentialDetailMeta):

        model = UserPasswordServerCredential
        widgets = {
            'name': forms.TextInput(),
            'username': forms.TextInput(),
            'password': forms.TextInput(),
            'server': forms.TextInput(),
        }
