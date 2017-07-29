"""
Supervisr Core Provider Forms
"""

import logging

from django import forms
from django.forms import ModelForm
from django.http import Http404
from django.utils.translation import ugettext as _

from supervisr.core.models import (APIKeyCredential, BaseCredential,
                                   UserPasswordCredential)
from supervisr.core.utils import path_to_class

LOGGER = logging.getLogger(__name__)

class ProviderForm(forms.Form):
    """
    Form create/edit a new Provider
    """

    title = 'General Information'

    name = forms.CharField(required=True, label=_('Instance Name'))
    provider_path = forms.ChoiceField(choices=[], required=True, label=_('Provider'))
    credentials = forms.ChoiceField(choices=[], required=True, label=_('Credentials'))

    def clean_credentials(self):
        """
        Import Provider and check if credentials are compatible
        """
        # Import provider based on form
        # also check in form if class exists and is subclass of BaseProvider
        _class = path_to_class(self.cleaned_data.get('provider_path'))
        # Get credentials
        creds = BaseCredential.objects.filter(name=self.cleaned_data.get('credentials'),
                                              owner=self.request.user)
        if not creds.exists():
            raise Http404
        r_creds = creds.first().cast()
        # Check if credentials work with provider
        prov_inst = _class(r_creds)
        LOGGER.info("About to provider.check_credentials")
        prov_inst.check_credentials(r_creds)
        return self.cleaned_data.get('credentials')

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

class NewCredentialAPIForm(ModelForm):
    """
    For to input credential details
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
