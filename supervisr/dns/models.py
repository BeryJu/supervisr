"""
Supervisr DNS Models
"""

from django.conf import settings
from django.db import models

from supervisr.core.models import (CreatedUpdatedModel, Domain, Product,
                                   ProviderInstance)

RECORD_TYPES = (
    ('A', 'A'),
    ('AAAA', 'AAAA'),
    ('AFSDB', 'AFSDB'),
    ('APL', 'APL'),
    ('CAA', 'CAA'),
    ('CDNSKEY', 'CDNSKEY'),
    ('CDS', 'CDS'),
    ('CERT', 'CERT'),
    ('CNAME', 'CNAME'),
    ('DHCID', 'DHCID'),
    ('DLV', 'DLV'),
    ('DNAME', 'DNAME'),
    ('DNSKEY', 'DNSKEY'),
    ('DS', 'DS'),
    ('HIP', 'HIP'),
    ('IPSECKEY', 'IPSECKEY'),
    ('KEY', 'KEY'),
    ('KX', 'KX'),
    ('LOC', 'LOC'),
    ('MX', 'MX'),
    ('NAPTR', 'NAPTR'),
    ('NS', 'NS'),
    ('NSEC', 'NSEC'),
    ('NSEC3', 'NSEC3'),
    ('NSEC3PARAM', 'NSEC3PARAM'),
    ('OPENPGPKEY', 'OPENPGPKEY'),
    ('PTR', 'PTR'),
    ('RRSIG', 'RRSIG'),
    ('RP', 'RP'),
    ('SIG', 'SIG'),
    ('SOA', 'SOA'),
    ('SRV', 'SRV'),
    ('SSHFP', 'SSHFP'),
    ('TA', 'TA'),
    ('TKEY', 'TKEY'),
    ('TLSA', 'TLSA'),
    ('TSIG', 'TSIG'),
    ('TXT', 'TXT'),
    ('URI', 'URI'),
)


class Comment(CreatedUpdatedModel):
    """
    DNS Zone Comments
    """
    zone_id = models.ForeignKey('Zone', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.CharField(max_length=40)
    comment = models.TextField()

class CryptoKey(models.Model):
    """
    DNS CryptoKeys for DNSSec
    """
    zone_id = models.ForeignKey('Zone', on_delete=models.CASCADE)
    flags = models.IntegerField()
    active = models.BooleanField()
    content = models.TextField()

class DomainMetadata(models.Model):
    """
    DNS Additional Domain Metadata
    """
    zone_id = models.ForeignKey('Zone', on_delete=models.CASCADE)
    kind = models.CharField(max_length=32)
    content = models.TextField()

class Zone(Product):
    """
    DNS Zone
    """
    domain = models.OneToOneField(Domain, on_delete=models.CASCADE)
    provider = models.ForeignKey(ProviderInstance, default=None, on_delete=models.CASCADE)
    master = models.CharField(max_length=128)
    last_check = models.IntegerField(default=0)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(default=0)
    account = models.CharField(max_length=40)
    enabled = models.BooleanField(default=True)

    @property
    def soa(self):
        """Get SOA record for this zone

        Returns None if no SOA Record exists
        """
        soa_records = Record.objects.filter(domain=self, type='SOA')
        if soa_records.exists():
            assert len(soa_records) == 1
            return soa_records.first()
        return None

    def __str__(self):
        return "Zone %s" % self.domain.domain

class Record(Product):
    """
    DNS Record
    """
    domain = models.ForeignKey(Zone, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=RECORD_TYPES)
    content = models.TextField()
    ttl = models.IntegerField(default=3600)
    prio = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    ordername = models.CharField(max_length=255, null=True, default=None)
    auth = models.IntegerField(default=1)

    @property
    def to_bind(self):
        """Return this record bind formatted"""
        return "%s IN %s %s" % (self.name, self.type, self.content)

    def __str__(self):
        return "Record %s" % self.name

class SuperMaster(models.Model):
    """
    DNS SuperMaster
    """
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
