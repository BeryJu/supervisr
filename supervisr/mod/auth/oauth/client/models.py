"""
OAuth Client models
"""

from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from supervisr.core.fields import EncryptedField
from supervisr.mod.auth.oauth.client.clients import get_client


# pylint: disable=too-few-public-methods
class ProviderManager(models.Manager):
    "Additional manager methods for Providers."

    def get_by_natural_key(self, name):
        """
        Get Neutral Keys
        """
        return self.get(name=name)


class Provider(models.Model):
    "Configuration for OAuth provider."

    name = models.CharField(max_length=50, unique=True)
    ui_name = models.TextField(default='')
    request_token_url = models.CharField(blank=True, max_length=255)
    authorization_url = models.CharField(max_length=255)
    access_token_url = models.CharField(max_length=255)
    profile_url = models.CharField(max_length=255)
    consumer_key = EncryptedField(blank=True, null=True, default=None)
    consumer_secret = EncryptedField(blank=True, null=True, default=None)

    objects = ProviderManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.consumer_key = self.consumer_key or None
        self.consumer_secret = self.consumer_secret or None
        super(Provider, self).save(*args, **kwargs)

    def natural_key(self):
        """
        Get Neutral Key
        """
        return (self.name, )

    def enabled(self):
        """
        Get enabled state
        """
        return self.consumer_key is not None and self.consumer_secret is not None
    enabled.boolean = True


# pylint: disable=too-few-public-methods
class AccountAccessManager(models.Manager):
    "Additional manager for AccountAccess models."

    def get_by_natural_key(self, identifier, provider):
        """
        Get neutral key
        """
        provider = Provider.objects.get_by_natural_key(provider)
        return self.get(identifier=identifier, provider=provider)


class AccountAccess(models.Model):
    "Authorized remote OAuth provider."

    identifier = models.CharField(max_length=255)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    access_token = EncryptedField(blank=True, null=True, default=None)

    objects = AccountAccessManager()

    class Meta:
        unique_together = ('identifier', 'provider')

    def __str__(self):
        return '{0} {1}'.format(self.provider, self.identifier)

    def save(self, *args, **kwargs):
        self.access_token = self.access_token or None
        super(AccountAccess, self).save(*args, **kwargs)

    def natural_key(self):
        """
        Get Neutral Keys
        """
        return (self.identifier, ) + self.provider.natural_key()
    natural_key.dependencies = ['supervisr_mod_auth_oauth_client.provider']

    @property
    def api_client(self):
        """
        Get API Client
        """
        return get_client(self.provider, self.access_token or '')
