"""
Supervisr Namecheap Domain Provider
"""

from supervisr.core.providers.domain import DomainProvider

from .core import NamecheapProvider


class NamecheapDomainProvider(DomainProvider, NamecheapProvider):
    """
    Namecheap domain provider
    """

    ui_name = 'Namecheap Domain'

    def register(self, domain):
        pass
        # return self.api.domains_create(
        #     DomainName = 'registeringadomainthroughtheapiwow.com',
        #     FirstName = 'Jack',
        #     LastName = 'Trotter',
        #     Address1 = 'Ridiculously Big Mansion, Yellow Brick Road',
        #     City = 'Tokushima',
        #     StateProvince = 'Tokushima',
        #     PostalCode = '771-0144',
        #     Country = 'Japan',
        #     Phone = '+81.123123123',
        #     EmailAddress = 'jack.trotter@example.com'
        # )

    def check_available(self, domain):
        pass

    def check_expiry(self, domain):
        pass

    def import_domains(self):
        pass
