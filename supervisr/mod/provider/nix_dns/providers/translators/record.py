"""supervisr mod provider PowerDNS Record Translator"""
from typing import Generator

from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import Record
from supervisr.mod.provider.nix_dns.models import Domain as PDNSDomain
from supervisr.mod.provider.nix_dns.models import Record as PDNSRecord


class PowerDNSRecordObject(ProviderObject):
    """PowerDNS intermediate Record object"""

    account = None
    internal = None

    def __init__(self, internal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        domains = PDNSDomain.objects.filter(name=internal.record_zone.domain.domain_name)
        if not domains.exists():
            raise ProviderObjectNotFoundException()
        self.domain = domains.first()

    def save(self, created: bool) -> ProviderResult:
        """Save this instance"""
        update_count = 0
        for resource in self.internal.resource_set.resources:
            _obj, updated = PDNSRecord.objects.update_or_create(
                name=self.internal.fqdn,
                domain=self.domain,
                defaults={
                    'type': resource.type,
                    'content': resource.content,
                    'ttl': resource.ttl,
                    'prio': resource.priority
                }
            )
            if updated:
                update_count += 1
        if update_count > 0:
            return ProviderResult.SUCCESS_UPDATED
        return ProviderResult.SUCCESS_CREATED

    def delete(self) -> ProviderResult:
        """Delete this instance"""
        PDNSRecord.objects.filter(
            name=self.internal.fqdn,
            domain=self.domain).delete()
        return ProviderResult.SUCCESS


class PowerDNSRecordTranslator(ProviderObjectTranslator[Record]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: Record) -> Generator[PowerDNSRecordObject, None, None]:
        """Convert Record to PDNS Record"""
        yield PowerDNSRecordObject(
            translator=self,
            internal=internal
        )
