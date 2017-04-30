"""
Supervisr Core Provider Forms
"""


from django import forms
from django.utils.translation import ugettext as _


class NewProviderForm(forms.Form):
    """
    Form create a new Provider
    """

    title = 'General Information'

    provider = forms.ChoiceField(choices=[], required=True,
                                 label=_('Provider'))
