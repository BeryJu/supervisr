"""
Supervisr Namecheap Domain Provider
"""

from supervisr.core.providers.base import (BaseProviderUIInterface,
                                           ProviderInterfaceAction)
from supervisr.core.providers.domain import DomainProvider
from supervisr.mod.namecheap.forms.domain import DoaminForm

from .core import NamecheapProvider, NamecheapProviderSetupUI


class NamecheapDomainProviderUIInterface(BaseProviderUIInterface):
    """
    Frontend for Namecheap Provider (Domain Setup)
    """

    def __init__(self, provider, action, request):
        super(NamecheapDomainProviderUIInterface, self).__init__(provider, action, request)

        if action == ProviderInterfaceAction.create:
            domain_form = DoaminForm()
            setattr(domain_form, 'provider', self.provider)
            self.forms = [domain_form]

    def post_submit(self, form_data):
        print(form_data)

class NamecheapDomainProvider(DomainProvider, NamecheapProvider):
    """
    Namecheap domain provider
    """

    ui_name = 'Namecheap Domain'
    interface_ui = NamecheapDomainProviderUIInterface
    setup_ui = NamecheapProviderSetupUI

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
