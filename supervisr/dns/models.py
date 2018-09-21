"""Supervisr DNS Models"""
from ipaddress import ip_address
from typing import Generator

from django.db import models

from supervisr.core.models import (CastableModel, Domain, ProviderAcquirable,
                                   ProviderTriggerMixin, UserAcquirable,
                                   UUIDModel)

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
    ('SRV', 'SRV'),
    ('SSHFP', 'SSHFP'),
    ('TA', 'TA'),
    ('TKEY', 'TKEY'),
    ('TLSA', 'TLSA'),
    ('TSIG', 'TSIG'),
    ('TXT', 'TXT'),
    ('URI', 'URI'),
)


class BaseZone(UUIDModel, CastableModel):
    """Base Zone fields"""

    soa_mname = models.TextField()
    soa_rname = models.TextField()
    soa_serial = models.IntegerField()
    soa_refresh = models.IntegerField(default=86400)
    soa_retry = models.IntegerField(default=7200)
    soa_expire = models.IntegerField(default=3600000)
    soa_ttl = models.IntegerField(default=172800)
    enabled = models.BooleanField(default=True)
    records = models.ManyToManyField('BaseRecord', blank=True)

    class Meta:

        abstract = True


class Zone(BaseZone, ProviderAcquirable, UserAcquirable):
    """DNS Zone"""

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    def __str__(self):
        return self.domain.domain_name


class ReverseZone(BaseZone, ProviderAcquirable, UserAcquirable):
    """Reverse DNS Zone for IPv4 and IPv6"""

    zone_ip = models.GenericIPAddressField(unpack_ipv4=True)
    netmask = models.IntegerField()

    @property
    def zone_name(self):
        """Get .arpa name"""
        return ip_address(self.zone_ip).reverse_pointer

    def __str__(self):
        return self.zone_ip


class BaseRecord(UUIDModel, UserAcquirable, ProviderTriggerMixin):
    """Base DNS Record"""

    name = models.TextField()
    enabled = models.BooleanField(default=True)

    @property
    def provider_instances(self) -> Generator['ProviderInstance', None, None]:
        """Return all provider instances that should be triggered"""
        from supervisr.core.utils.models import walk_m2m
        for zone in walk_m2m(self.cast(), only_classes=[Zone]):
            for provider in zone.provider_instances:
                yield provider

    def __str__(self):
        if self.cast() != self:
            return self.cast().__str__()
        return self.name


class SetRecord(BaseRecord):
    """DNS Record pointing to a collection of other Records. Can be recursive."""

    append_name = models.BooleanField(default=False)
    records = models.ManyToManyField('BaseRecord', blank=True, related_name='set')

    def __str__(self):
        return "Set %s" % self.name

class DataRecord(BaseRecord):
    """DNS Record pointing to a single Address/"""

    type = models.CharField(max_length=10, choices=RECORD_TYPES)
    content = models.TextField()
    ttl = models.IntegerField(default=3600)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return "%s (type=%s content=%s)" % (self.name, self.type, self.content)
