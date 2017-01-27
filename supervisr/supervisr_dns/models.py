"""
Supervisr DNS Models
"""
from django.db import models

from supervisr.models import CreatedUpdatedModel, Domain, Product


class DNSZone(Product):
    """
    Store Information about a root DNS Zone
    """
    domain_dns = models.OneToOneField(Domain)
    zone = models.CharField(max_length=255) # 255 Bytes acording to rfc1035, 2.3.4

    @property
    def domain(self):
        """
        Get our parent domain
        """
        return self.domain_dns

    @domain.setter
    def domain(self, value):
        self.domain_dns = value

    def __str__(self):
        return "DNS Zone '%s'" % self.zone

class DNSRecord(CreatedUpdatedModel):
    """
    Store a particular DNS record
    """
    zone = models.OneToOneField(DNSZone, primary_key=True, unique=True)
    type = models.CharField(max_length=10, default='A')
    ttl = models.IntegerField()
    prio = models.IntegerField()
    content = models.TextField()

    def __str__(self):
        return "DNS Record for '%s': '%s %s'" % \
            (self.zone, self.type, self.content)
