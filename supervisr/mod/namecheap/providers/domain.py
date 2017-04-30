"""
Supervisr Namecheap Domain Provider
"""

from supervisr.core.providers.base import (BaseProviderUIInterface,
                                           ProviderInterfaceAction)
from supervisr.core.providers.domain import DomainProvider
from supervisr.mod.namecheap.forms.domain import DoaminForm
from supervisr.mod.namecheap.providers.core import NamecheapProvider


class NamecheapDomainProvider(DomainProvider):
    """
    Namecheap domain provider
    """

    interface_ui = NamecheapDomainProviderUIInterface

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


class NamecheapDomainProviderUIInterface(BaseProviderUIInterface):

    def __init__(self, provider, action, request):
        super(NamecheapDomainProviderUIInterface, self).__init__(provider, action, request)

        if action == ProviderInterfaceAction.create:
            domain_form = DoaminForm()
            setattr(domain_form, 'provider', self.provider)
            self.forms = [domain_form]

    def post_submit(self, form_data) -> Any:
        print(form_data)
        # self.provider.register(
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
        #     )
