"""
Supervisr DNS Models
"""

from django.db import models

from supervisr.core.models import Domain, Product, ProviderInstance


class Comments(models.Model):
    """
    PowerDNS Comments
    """
    domain = models.ForeignKey('DNSDomain')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    modified_at = models.IntegerField()
    account = models.CharField(max_length=40, blank=True, null=True)
    comment = models.CharField(max_length=65535)

    class Meta:
        db_table = 'comments'


class Cryptokeys(models.Model):
    """
    PowerDNS Cryptokeys
    """
    domain = models.ForeignKey('DNSDomain', blank=True, null=True)
    flags = models.IntegerField()
    active = models.NullBooleanField()
    content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cryptokeys'


class DomainMetadata(models.Model):
    """
    PowerDNS DomainMetadata
    """
    domain = models.ForeignKey('DNSDomain', blank=True, null=True)
    kind = models.CharField(max_length=32, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'domainmetadata'


class DNSDomain(Product):
    """
    PowerDNS Domains
    """
    domain = models.OneToOneField(Domain)
    provider = models.ForeignKey(ProviderInstance, default=None)
    master = models.CharField(max_length=128, blank=True, null=True)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'DNSDomain'

    def __str__(self):
        return "DNS Domain %s" % self.domain


class Record(Product):
    """
    PowerDNS Records
    """
    domain = models.ForeignKey('DNSDomain', blank=True, null=True, db_column='domain_id')
    type = models.CharField(max_length=10, blank=True, null=True)
    content = models.CharField(max_length=65535, blank=True, null=True)
    ttl = models.IntegerField(blank=True, null=True)
    prio = models.IntegerField(blank=True, null=True)
    change_date = models.IntegerField(blank=True, null=True)
    disabled = models.NullBooleanField()
    ordername = models.CharField(max_length=255, blank=True, null=True)
    auth = models.NullBooleanField()

    class Meta:
        db_table = 'records'

    def __str__(self):
        return "%s.%s/%s@%s" % (self.name, self.domain.name, self.type, self.content)

class SuperMasters(models.Model):
    """
    PowerDNS SuperMasters
    """
    # pylint: disable=invalid-name
    ip = models.GenericIPAddressField(primary_key=True)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40)

    class Meta:
        db_table = 'supermasters'
        unique_together = (('ip', 'nameserver'),)

class TSIGKeys(models.Model):
    """
    PowerDNS TSIGKeys
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    algorithm = models.CharField(max_length=50, blank=True, null=True)
    secret = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tsigkeys'
        unique_together = (('name', 'algorithm'),)
