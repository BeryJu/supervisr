"""
Supervisr Core Domain Forms
"""

import logging
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import Domain, ProviderInstance
from supervisr.core.regex import DOMAIN_REGEX

LOGGER = logging.getLogger(__name__)

class DomainForm(forms.ModelForm):
    """Form create a new Domain"""

    title = 'General Information'

    def clean_domain(self):
        """Import Provider and check if domain can be created"""
        # Check if domain matches domain_regex
        if not re.match(r'^%s$' % DOMAIN_REGEX, self.cleaned_data.get('domain')):
            LOGGER.debug("Domain didn't match regex")
            raise forms.ValidationError(_('Domain name is not valid'))
        # Import provider based on form
        # also check in form if class exists and is subclass of BaseProvider
        provider = ProviderInstance.objects.filter(
            pk=self.cleaned_data.get('provider'),
            userproductrelationship__user__in=[self.request.user])
        if not provider.exists():
            LOGGER.debug("Invalid Provider Instance")
            raise ValidationError("Invalid Provider Instance")
        r_prov_inst = provider.first().provider
        r_prov_dom_inst = r_prov_inst.domain_provider(provider.first().credentials)
        LOGGER.debug("About to provider.check_available")
        r_prov_dom_inst.check_available(self.cleaned_data.get('domain'))
        return self.cleaned_data.get('domain')

    class Meta:

        model = Domain
        fields = ['provider', 'domain']
        labels = {
            'provider': _('Provider (Registrar)'),
        }
