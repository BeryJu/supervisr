"""
Supervisr DNS Models
"""

from uuid import uuid4

from django.conf import settings
from django.db import models

from supervisr.core.models import (CreatedUpdatedModel, Domain,
                                   ProviderAcquirable, UserAcquirable)

# imported from powerdns
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

class Zone(ProviderAcquirable, UserAcquirable):
    """DNS Zone"""

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    soa = models.ForeignKey('Resource', on_delete=models.CASCADE)

    def __str__(self):
        return "Zone %s" % self.domain.domain_name

class Record(UserAcquirable):
    """DNS Record"""

    name = models.TextField()
    record_zone = models.ForeignKey('Zone', on_delete=models.CASCADE)
    resource_set = models.ForeignKey('ResourceSet', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid4)

    def __str__(self):
        return "Record %s" % self.name

class Resource(UserAcquirable):
    """Record Resource"""

    name = models.TextField()
    type = models.CharField(max_length=10, choices=RECORD_TYPES)
    content = models.TextField()
    ttl = models.IntegerField(default=3600)
    priority = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid4)

    def __str__(self):
        return "RecordData %s %s" % (self.type, self.content)

class ResourceSet(UserAcquirable):
    """Connect Record to Resource"""

    uuid = models.UUIDField(default=uuid4)
    name = models.TextField()
    resource = models.ManyToManyField('Resource', blank=True)

    def __str__(self):
        return "ResourceSet %s" % self.name
