"""
Supervisr Core Domain Forms
"""


import logging

from django import forms
from django.core.exceptions import ValidationError

from supervisr.core.providers.base import BaseProviderInstance

LOGGER = logging.getLogger(__name__)

class DomainForm(forms.Form):
    """
    Form create a new Domain
    """

    title = 'General Information'

    provider = forms.ChoiceField(label='Provider (Registrar)')
    domain = forms.CharField(label='Domain')

    def clean_domain(self):
        """
        Import Provider and check if domain can be created
        """
        # Import provider based on form
        # also check in form if class exists and is subclass of BaseProvider
        provider = BaseProviderInstance.objects.filter(
            uuid=self.cleaned_data.get('provider'),
            userproductrelationship__user__in=[self.request.user])
        if not provider.exists():
            raise ValidationError("Invalid Provider Instance")
        r_prov_inst = provider.first().provider
        r_prov_dom_inst = r_prov_inst.domain_provider(provider.first().credentials)
        LOGGER.info("About to provider.check_available")
        r_prov_dom_inst.check_available(self.cleaned_data.get('domain'))
        return self.cleaned_data.get('domain')
