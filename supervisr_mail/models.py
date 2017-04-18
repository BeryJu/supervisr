"""
Supervisr Web Models
"""
import logging

from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from passlib.hash import sha512_crypt

from supervisr.models import (CreatedUpdatedModel, Domain, Product,
                              UserProductRelationship)
from supervisr.signals import (SIG_DOMAIN_CREATED,
                               SIG_USER_PRODUCT_RELATIONSHIP_CREATED)

LOGGER = logging.getLogger(__name__)


class MailDomain(Product):
    """
    Stores information about a MailDomain
    """

    domain_mail = models.OneToOneField(Domain)

    domain_raw = models.TextField(blank=True, help_text=_('This field is automatically generated'
                                                          'by Django to make queries easier.'))
    enabled = models.BooleanField(default=True)

    @property
    def domain(self):
        """
        Get our parent domain
        """
        return self.domain_mail

    @domain.setter
    def domain(self, value):
        self.domain_mail = value

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw
        """
        if self.domain_raw is not self.domain_mail.name:
            self.domain_raw = self.domain_mail.name
        super(MailDomain, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.domain)

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
    domain_mail = models.ForeignKey(MailDomain)
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
    def domain(self):
        """
        Get our parent domain
        """
        return self.domain_mail

    @domain.setter
    def domain(self, value):
        self.domain_mail = value

    @property
    def email(self):
        """
        Get our full address
        """
        return self.email_raw

    def set_password(self, new_password, salt=None):
        """
        Sets a new password with a new salt
        """
        self.password = sha512_crypt.hash(new_password, salt=salt)
        LOGGER.info("Updated Password MailAccount %s", self.email)
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw and email_raw
        """
        domain = str(self.domain_mail.domain)
        if self.domain_raw is not domain:
            self.domain_raw = domain
        if self.email_raw is not '%s@%s' % (self.address, domain):
            self.email_raw = '%s@%s' % (self.address, domain)
        super(MailAccount, self).save(*args, **kwargs)

    def __str__(self):
        return "%s@%s" % (self.address, self.domain_mail)

class MailForwarder(CreatedUpdatedModel):
    """
    Record to save destinations to forward mail to
    """

    account = models.ForeignKey(MailAccount)
    destination = models.EmailField()

    def __str__(self):
        return "%s => %s" % (self.account.address, self.destination)

@receiver(SIG_DOMAIN_CREATED)
# pylint: disable=unused-argument
def mail_handle_domain_created(sender, signal, domain, **kwargs):
    """
    Create a MailDomain when a Domain is created
    """
    MailDomain.objects.create(
        name=domain.name,
        description='MailDomain %s' % domain.name,
        domain_mail=domain)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument
def mail_handle_upr_created(sender, signal, upr, **kwargs):
    """
    Create upr's when UPR from domains are created
    """
    if upr.product.__class__ == Domain:
        # Only create UPR if it's from a domain
        UserProductRelationship.objects.create(
            product=MailDomain.objects.get(domain_mail=upr.product),
            user=upr.user)
