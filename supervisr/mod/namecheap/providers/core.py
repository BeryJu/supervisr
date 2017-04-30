
from django.conf import settings
from django.db import models
from namecheap import Api

from supervisr.core.providers.base import (BaseProvider, BaseProviderInstance,
                                           BaseProviderUIInterface,
                                           ProviderInterfaceAction)
from supervisr.mod.namecheap.forms.setup import SetupForm


class NamecheapProviderSetupUI(BaseProviderUIInterface):

    def __init__(self, provider, action, request):
        super(NamecheapProviderSetupUI, self).__init__(provider, action, request)

        if action == ProviderInterfaceAction.create:
            setup_form = SetupForm()
            setattr(setup_form, 'provider', self.provider)
            self.forms = [setup_form]

    def post_submit(self, form_data):
        print(form_data)

class NamecheapProvider(BaseProvider):
    """
    Namecheap provider
    """
    ui_name = 'Namecheap'
    interface_ui = NamecheapProviderSetupUI

    api = None

    def __init__(self):
        super(NamecheapProvider, self).__init__()
        self.api = Api(self.api_username, self.api_key, self.username, ip_address, sandbox=self.sandbox)

class NamecheapProviderInstance(BaseProviderInstance):

    # Fields
    api_key = models.TextField()
    api_username = models.TextField()
    username = models.TextField()
    sandbox = models.BooleanField(default=settings.DEBUG)
