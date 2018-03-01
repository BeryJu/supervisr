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

    def clean_domain_name(self):
        """Import Provider and check if domain can be created"""
        # Check if domain matches domain_regex
        if not re.match(r'^%s$' % DOMAIN_REGEX, self.cleaned_data.get('domain_name')):
            LOGGER.debug("Domain didn't match regex")
            raise forms.ValidationError(_('Domain name is not valid'))
        return self.cleaned_data.get('domain_name')

    class Meta:

        model = Domain
        fields = ['provider_instance', 'domain_name', 'is_sub']
        labels = {
            'provider_instance': _('Provider (Registrar)'),
        }
