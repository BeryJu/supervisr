"""
Supervisr Core Provider Forms
"""


from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from supervisr.core.models import APIKeyCredential, UserPasswordCredential


class NewProviderForm(forms.Form):
    """
    Form create a new Provider
    """

    title = 'General Information'

    provider = forms.ChoiceField(choices=[], required=True,
                                 label=_('Provider'))

class NewCredentialForm(forms.Form):
    """
    Form create a new Credential
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
