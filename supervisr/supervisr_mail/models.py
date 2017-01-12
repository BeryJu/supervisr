from django.db import models
from django.contrib.auth.models import User
from supervisr.models import Product, Domain

class MailDomain(Product):
    domain_mail = models.OneToOneField(Domain)

    @property
    def domain(self):
        return self.domain_mail

    @domain.setter
    def domain(self, value):
        self.domain_mail = value

class MailAccount(Product):
    address = models.CharField(max_length=64) # rfc5321 4.5.3.1.1.
    quota = models.BigIntegerField(default=0) # account quota in MB. 0 == unlimited
    can_send = models.BooleanField(default=True)
    password = models.CharField(max_length=128)