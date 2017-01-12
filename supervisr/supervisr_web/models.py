from django.db import models
from django.contrib.auth.models import User
from supervisr.models import Product, Domain, UserProfile

class WebDomain(Product):
    domain_web = models.OneToOneField(Domain)
    root = models.TextField()
    profile = models.ForeignKey(UserProfile)
    quota = models.BigIntegerField(default=0) # domain quota in MB. 0 == unlimited
    is_php_enabled = models.BooleanField(default=True)
    custom_config = models.TextField()

    @property
    def domain(self):
        return self.domain_web

    @domain.setter
    def domain(self, value):
        self.domain_web = value

    def __str__(self):
        return "WebDomain %s" % self.domain