"""
Supervisr Namecheap Provider
"""

from django.conf import settings
from django.db import models
from namecheap import Api

from supervisr.core.providers.base import (BaseProvider, BaseProviderInstance,
                                           BaseProviderUIInterface)
from supervisr.mod.namecheap.forms.setup import SetupForm


class NamecheapProviderSetupUI(BaseProviderUIInterface):
    """
    Frontend for Namecheap Provider (API Setup)
    """

    forms = [SetupForm]

    def post_submit(self, form_data):
        print(form_data)

# pylint: disable=too-few-public-methods
class NamecheapProvider(BaseProvider):
    """
    Namecheap provider
    """

    api = None
    setup_ui = NamecheapProviderSetupUI


    def __init__(self, instance):
        super(NamecheapProvider, self).__init__(instance)
        self.api = Api(
            self.instance.api_username,
            self.instance.api_key,
            self.instance.username,
            '',
            sandbox=self.instance.sandbox)

class NamecheapProviderInstance(BaseProviderInstance):
    """
    Data to be saved with a Namecheap Provider instance
    """

    # Fields
    api_key = models.TextField()
    api_username = models.TextField()
    username = models.TextField()
    sandbox = models.BooleanField(default=settings.DEBUG)