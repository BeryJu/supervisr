"""supervisr libcloud models"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from supervisr.core.fields import EncryptedField
from supervisr.core.models import BaseCredential


def provider_tuple():
    """Make a tuple of all libcloud-supported providers"""
    def providers_for_class(cls):
        """Get all Providers for a single Part of libcloud"""
        provider_selection = []
        for provider in dir(cls):
            if not provider.startswith('__'):
                provider_selection.append((provider.lower(),
                                           provider.capitalize().replace('_', ''),))
        return provider_selection
    from libcloud.dns.types import Provider as dns_providers
    return (
        ('DNS', providers_for_class(dns_providers),),
    )

class LibCloudCredentials(BaseCredential):
    """libcloud Provider Credentials. Modeled after
    https://libcloud.readthedocs.io/en/latest/apidocs/libcloud.common.html#libcloud.common.base.BaseDriver"""

    key = EncryptedField()
    secret = EncryptedField(null=True, blank=True, default=None)
    provider = models.TextField(choices=provider_tuple())
    secure = models.BooleanField(default=True)
    host = models.TextField(null=True, blank=True, default=None)
    port = models.IntegerField(null=True, blank=True, default=None)
    api_version = models.TextField(null=True, blank=True, default=None)
    region = models.TextField(null=True, blank=True, default=None)
    form = 'supervisr.provider.libcloud.forms.LibcloudCredentialForm'

    @staticmethod
    def type():
        return _('libcloud Credentials')
