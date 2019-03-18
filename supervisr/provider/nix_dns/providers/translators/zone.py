"""supervisr mod provider PowerDNS Zone Translator"""
from typing import Generator

from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import BaseZone
from supervisr.provider.nix_dns.models import Domain as PDNSDomain
from supervisr.provider.nix_dns.models import Record as PDNSRecord


class PowerDNSZoneObject(ProviderObject):
    """PowerDNS intermediate Zone object"""

    account = None
    internal = None

    def __make_soa_content(self, zone: BaseZone) -> str:
        """Get SOA content string for record"""
        return "%s %s %d %d %d %d %d" % (
            zone.soa_mname,
            zone.soa_rname,
            int(zone.soa_serial),
            int(zone.soa_refresh),
            int(zone.soa_retry),
            int(zone.soa_expire),
            int(zone.soa_ttl),
        )

    def save(self, **kwargs) -> ProviderResult:
        """Save this instance"""
        domain, updated = PDNSDomain.objects.update_or_create(
            name=self.internal.zone_name)
        _soa, _soa_updated = PDNSRecord.objects.update_or_create(
            domain=domain,
            name=domain.name,
            type='SOA',
            content=self.__make_soa_content(self.internal))
        if updated:
            return ProviderResult.SUCCESS_UPDATED
        return ProviderResult.SUCCESS_CREATED

    def delete(self, **kwargs) -> ProviderResult:
        """Delete this instance"""
        # Delete domain
        existing = PDNSDomain.objects.filter(name=self.internal.zone_name)
        if not existing.exists():
            raise ProviderObjectNotFoundException()
        domain = existing.first()
        # Delete all records referencing this domain, to make sure nothing is forgot
        PDNSRecord.objects.filter(domain=domain).delete()
        domain.delete()
        return ProviderResult.SUCCESS


class PowerDNSZoneTranslator(ProviderObjectTranslator[BaseZone]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: BaseZone) -> Generator[PowerDNSZoneObject, None, None]:
        """Convert Zone to Domain"""
        yield PowerDNSZoneObject(
            translator=self,
            internal=internal)
