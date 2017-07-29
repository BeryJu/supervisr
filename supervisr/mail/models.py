"""
Supervisr Web Models
"""
import logging

from django.db import models
from django.utils.translation import ugettext as _
from passlib.hash import sha512_crypt

from supervisr.core.models import (CreatedUpdatedModel, Domain, Event, Product,
                                   ProviderInstance)

LOGGER = logging.getLogger(__name__)


class MailDomain(Product):
    """
    Stores information about a MailDomain
    """

    domain = models.OneToOneField(Domain)
    provider = models.ForeignKey(ProviderInstance, default=None)
    domain_raw = models.TextField(blank=True, help_text=_('This field is automatically generated'
                                                          'by Django to make queries easier.'))
    enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw
        """
        if self.domain_raw is not self.domain.domain:
            self.domain_raw = self.domain.domain
        super(MailDomain, self).save(*args, **kwargs)

    def __str__(self):
        return "Mail Domain %s" % self.domain

    @property
    def has_catchall(self):
        """
        Return true if this domain has a catch all account
        """
        return self.mailaccount_set.filter(is_catchall=True).exists()

class MailAccount(Product):
    """
    Store information about a MailAccount/MailForward
    """
    address = models.CharField(max_length=64) # rfc5321 4.5.3.1.1.
    domain = models.ForeignKey(MailDomain)
    quota = models.BigIntegerField(default=0) # account quota in MB. 0 == unlimited
    size = models.BigIntegerField(default=0)
    can_send = models.BooleanField(default=True)
    can_receive = models.BooleanField(default=True)
    password = models.CharField(max_length=128, blank=True)
    is_catchall = models.BooleanField(default=False)

    domain_raw = models.TextField(blank=True, help_text=_('This field is automatically generated'
                                                          'by Django to make queries easier.'))
    email_raw = models.TextField(blank=True, help_text=_('This field is automatically generated'
                                                         'by Django to make queries easier.'))

    @property
    def email(self):
        """
        Get our full address
        """
        return self.email_raw

    def set_password(self, invoker, new_password, salt=None, request=None):
        """
        Sets a new password with a new salt
        """
        self.password = sha512_crypt.hash(new_password, salt=salt)
        LOGGER.info("Updated Password MailAccount %s", self.email)
        Event.create(
            user=invoker,
            message=_("Changed Password for Mail Account %(account)s" % {'account':str(self)}),
            request=request)
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw and email_raw
        """
        domain = str(self.domain.domain.domain)
        self.domain_raw = domain
        if self.email_raw is not '%s@%s' % (self.address, domain):
            self.email_raw = '%s@%s' % (self.address, domain)
        super(MailAccount, self).save(*args, **kwargs)

    def __str__(self):
        return "%s@%s" % (self.address, self.domain.domain.domain)

    def search_title(self):
        """
        Return email address for search results
        """
        return self.email

    class Meta:

        sv_search_fields = ['address', 'email_raw']

class MailAlias(CreatedUpdatedModel):
    """
    Record to save destinations to forward mail to
    """

    account = models.ForeignKey(MailAccount)
    destination = models.EmailField()

    def __str__(self):
        return "%s => %s" % (self.account.email_raw, self.destination)
