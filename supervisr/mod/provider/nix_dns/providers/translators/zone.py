"""supervisr mod provider PowerDNS Zone Translator"""
from typing import Generator

from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import Zone
from supervisr.mod.provider.nix_dns.models import Domain as PDNSDomain


class PowerDNSZoneObject(ProviderObject):
    """PowerDNS intermediate Zone object"""

    account = None

    def save(self, created: bool) -> ProviderResult:
        """Save this instance"""
        _obj, updated = PDNSDomain.objects.update_or_create(
            pk=self.id,
            defaults={
                'name': self.name,
                'account': self.account
            })
        if updated:
            return ProviderResult.SUCCESS_UPDATED
        return ProviderResult.SUCCESS_CREATED

    def delete(self) -> ProviderResult:
        """Delete this instance"""
        existing = PDNSDomain.objects.filter(name=self.name, pk=self.id)
        if not existing.exists():
            raise ProviderObjectNotFoundException()
        existing.first().delete()
        return ProviderResult.SUCCESS


class PowerDNSZoneTranslator(ProviderObjectTranslator[Zone]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: Zone) -> Generator[PowerDNSZoneObject, None, None]:
        """Convert Zone to Domain"""
        yield PowerDNSZoneObject(
            translator=self,
            id=internal.pk,
            name=internal.domain.domain_name
        )
