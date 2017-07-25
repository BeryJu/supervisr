"""
Supervisr DNS Models
"""

from django.contrib.auth.models import User
from django.db import models

from supervisr.core.models import (CreatedUpdatedModel, Domain, Product,
                                   ProviderInstance)


class Comment(CreatedUpdatedModel):
    """
    DNS Zone Comments
    """
    zone_id = models.ForeignKey('Zone')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    user = models.ForeignKey(User)
    account = models.CharField(max_length=40)
    comment = models.TextField()

class CryptoKey(models.Model):
    """
    DNS CryptoKeys for DNSSec
    """
    zone_id = models.ForeignKey('Zone')
    flags = models.IntegerField()
    active = models.BooleanField()
    content = models.TextField()

class DomainMetadata(models.Model):
    """
    DNS Additional Domain Metadata
    """
    zone_id = models.ForeignKey('Zone')
    kind = models.CharField(max_length=32)
    content = models.TextField()

class Zone(Product):
    """
    DNS Zone
    """
    domain = models.OneToOneField(Domain)
    provider = models.ForeignKey(ProviderInstance, default=None)
    master = models.CharField(max_length=128)
    last_check = models.IntegerField(default=0)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(default=0)
    account = models.CharField(max_length=40)
    enabled = models.BooleanField(default=True)

class Record(Product):
    """
    DNS Record
    """
    domain = models.ForeignKey(Zone)
    type = models.CharField(max_length=10)
    content = models.TextField()
    ttl = models.IntegerField(default=3600)
    prio = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    ordername = models.CharField(max_length=255, null=True, default=None)
    auth = models.IntegerField(default=1)

    def __str__(self):
        return "Record %s" % self.name

class SuperMaster(models.Model):
    """
    DNS SuperMaster
    """
    # pylint: disable=invalid-name
    ip = models.CharField(max_length=64)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40)

    class Meta:
        unique_together = (('ip', 'nameserver'),)

class TSIGKey(models.Model):
    """
    DNS TSIGKeys
    """
    name = models.CharField(max_length=255)
    algorithm = models.CharField(max_length=50)
    secret = models.CharField(max_length=255)

    class Meta:
        unique_together = (('name', 'algorithm'),)
