"""
Supervisr Web Models
"""

from django.db import models

from supervisr.core.models import Domain, Product, UserProfile


class WebDomain(Product):
    """
    Stores information about a Webdomain
    """

    domain_web = models.OneToOneField(Domain)
    root = models.TextField(default='/')
    profile = models.ForeignKey(UserProfile)
    quota = models.BigIntegerField(default=0) # domain quota in MB. 0 == unlimited
    is_php_enabled = models.BooleanField(default=True)
    custom_config = models.TextField(blank=True)

    @property
    def domain(self):
        """
        Get our parent domain
        """
        return self.domain_web

    @domain.setter
    def domain(self, value):
        self.domain_web = value

    def __str__(self):
        return "WebDomain %s" % self.domain
