"""
Supervisr Namecheap Domain Provider
"""

from django.conf import settings
from django.db import models

from supervisr.mod.namecheap.forms.domain import DoaminForm
from supervisr.core.providers.domain import DomainProvider
from namecheap import Api


class NamecheapDomainProvider(DomainProvider):
    """
    Namecheap domain provider
    """

    # Fields
    api_key = models.TextField()
    api_username = module.TextField()
    username = models.TextField()
    sandbox = models.BooleanField(default=settings.DEBUG)

    # Forms
    setup_form = [DoaminForm]

    api = None

    def __init__(self):
        super(NamecheapDomainProvider, self).__init__()
        api = Api(self.api_username, self.api_key, self.username, ip_address, sandbox=self.sandbox)

    def register(self, domain):
        return self.api.domains_create(
            DomainName = 'registeringadomainthroughtheapiwow.com',
            FirstName = 'Jack',
            LastName = 'Trotter',
            Address1 = 'Ridiculously Big Mansion, Yellow Brick Road',
            City = 'Tokushima',
            StateProvince = 'Tokushima',
            PostalCode = '771-0144',
            Country = 'Japan',
            Phone = '+81.123123123',
            EmailAddress = 'jack.trotter@example.com'
        )

    def check_available(self, domain):
        pass

    def check_expiry(self, domain):
        pass

    def import_domains(self):
        pass

