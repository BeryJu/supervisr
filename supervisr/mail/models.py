"""
Supervisr Web Models
"""
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from passlib.hash import sha512_crypt
from supervisr.core.models import (CreatedUpdatedModel, Domain, Event,
                                   ProviderAcquirable, User, UserAcquirable)

LOGGER = logging.getLogger(__name__)


class MailDomain(CreatedUpdatedModel, ProviderAcquirable, UserAcquirable):
    """Stores information about a MailDomain"""

    domain = models.OneToOneField(Domain, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return "Mail Domain %s" % self.domain

    @property
    def has_catchall(self):
        """
        Return true if this domain has a catch all account
        """
        return self.mailaccount_set.filter(is_catchall=True).exists()


class MailDomainAddressRelationship(CreatedUpdatedModel, UserAcquirable):
    """Store relationship between Address and MailDomains"""

    mail_domain = models.ForeignKey('MailDomain', on_delete=models.CASCADE)
    mail_address = models.ForeignKey('Address', on_delete=models.CASCADE)
    is_catchall = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)


class Address(CreatedUpdatedModel, ProviderAcquirable, UserAcquirable):
    """Single Mail address"""

    mail_address = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)
    domains = models.ManyToManyField('MailDomain', through='MailDomainAddressRelationship')

    def __str__(self):
        return "Address %s" % self.mail_address


class Forwarder(CreatedUpdatedModel, ProviderAcquirable, UserAcquirable):
    """Forwader from an address to a target"""

    source_address = models.ForeignKey('Address', on_delete=models.CASCADE)
    destination_address = models.EmailField()

    def __str__(self):
        return "Forwarder '%s' => '%s'" % (self.source_address, self.destination_address)


class AccountAddressRelationship(CreatedUpdatedModel, UserAcquirable):
    """Store relationship between Account and Address"""

    mail_account = models.ForeignKey('Account', on_delete=models.CASCADE)
    mail_address = models.ForeignKey('Address', on_delete=models.CASCADE)
    can_send = models.BooleanField(default=True)
    can_receive = models.BooleanField(default=True)


class Account(CreatedUpdatedModel, ProviderAcquirable, UserAcquirable):
    """Mail Account that stores mail"""

    name = models.TextField()
    addresses = models.ManyToManyField(Address, through=AccountAddressRelationship)
    quota = models.BigIntegerField(default=0)  # account quota in MB. 0 == unlimited
    size = models.BigIntegerField(default=0)
    password = models.CharField(max_length=128, blank=True)

    def set_password(self, invoker: User, new_password: str, salt: str = None, request=None):
        """Sets a new password with a new salt"""
        self.password = sha512_crypt.hash(new_password, salt=salt)
        LOGGER.debug("Updated Password Account %s", self.name)
        Event.create(
            user=invoker,
            message=_("Changed Password for Mail Account %(account)s" % {'account': str(self)}),
            request=request)
        self.save()

    def __str__(self):
        return "Account %s" % self.name
