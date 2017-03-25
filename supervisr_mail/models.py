"""
Supervisr Web Models
"""
import logging

from django.db import models
from django.utils.translation import ugettext as _
from passlib.hash import sha512_crypt

from supervisr.models import CreatedUpdatedModel, Domain, Product

LOGGER = logging.getLogger(__name__)


class MailDomain(Product):
    """
    Stores information about a MailDomain
    """

    domain_mail = models.OneToOneField(Domain)

    domain_raw = models.TextField(blank=True, help_text=_('This field is automatically generated'
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

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw
        """
        if self.domain_raw is not self.domain_mail.name:
            self.domain_raw = self.domain_mail.name
        super(MailDomain, self).save(*args, **kwargs)

    def __str__(self):
        return "MailDomain %s" % self.domain

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
    password = models.CharField(max_length=128)
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
        return "MailAccount %s %s" % (self.address, self.domain_mail)

class MailForwarder(CreatedUpdatedModel):
    """
    Record to save destinations to forward mail to
    """

    account = models.ForeignKey(MailAccount)
    destination = models.EmailField()

    def __str__(self):
        return "MailForwarder %s => %s" % (self.account.address, self.destination)
