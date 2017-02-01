"""
Supervisr Web Models
"""

from django.db import models
from django.utils.translation import ugettext as _

from supervisr.models import Domain, Product


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
        if self.domain_raw is not self.domain.name:
            self.domain_raw = self.domain.name
        super(MailDomain, self).save(*args, **kwargs)

    def __str__(self):
        return "MailDomain %s" % self.domain

class MailAccount(Product):
    """
    Store information about a MailAccount/MailForward
    """
    address = models.CharField(max_length=64) # rfc5321 4.5.3.1.1.
    domain_mail = models.ForeignKey(MailDomain)
    quota = models.BigIntegerField(default=0) # account quota in MB. 0 == unlimited
    can_send = models.BooleanField(default=True)
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

    def save(self, *args, **kwargs):
        """
        Override save to set domain_raw and email_raw
        """
        if self.domain_raw is not self.domain.name:
            self.domain_raw = self.domain.name
        if self.email_raw is not '%s@%s' % (self.address, self.domain.name):
            self.email_raw = '%s@%s' % (self.address, self.domain.name)
        super(MailAccount, self).save(*args, **kwargs)

    def __str__(self):
        return "MailAccount %s@%s" % (self.address, self.domain_mail)
