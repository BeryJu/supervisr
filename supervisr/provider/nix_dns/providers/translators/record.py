"""supervisr mod provider PowerDNS Record Translator"""
from logging import getLogger
from typing import Generator

from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.providers.compat import CompatDNSRecord
from supervisr.provider.nix_dns.models import Domain as PDNSDomain
from supervisr.provider.nix_dns.models import Record as PDNSRecord

LOGGER = getLogger(__name__)

class PowerDNSRecordObject(ProviderObject):
    """PowerDNS intermediate Record object"""

    internal = None

    def __init__(self, translator, internal, *args, **kwargs):
        self.internal = internal
        super().__init__(translator, *args, **kwargs)
        domains = PDNSDomain.objects.filter(name=internal.domain)
        if not domains.exists():
            raise ProviderObjectNotFoundException()
        self.domain = domains.first()

    def save(self, **kwargs) -> ProviderResult:
        """Save this instance"""
        LOGGER.debug("About to create %s (type=%s, content=%s)",
                     self.internal.name, self.internal.type, self.internal.content)
        _obj, updated = PDNSRecord.objects.update_or_create(
            name=self.internal.name,
            domain=self.domain,
            type=self.internal.type,
            content=self.internal.content,
            disabled=not self.internal.enabled,
            ttl=self.internal.ttl,
            prio=self.internal.priority,
            auth=1)
        if updated:
            return ProviderResult.SUCCESS_UPDATED
        return ProviderResult.SUCCESS_CREATED

    def delete(self, **kwargs) -> ProviderResult:
        """Delete this instance"""
        LOGGER.debug("About to delete %s (type=%s, content=%s)",
                     self.internal.name, self.internal.type, self.internal.content)
        delete_count, _obj = PDNSRecord.objects.filter(
            name=self.internal.name,
            domain=self.domain,
            type=self.internal.type,
            content=self.internal.content,
            disabled=not self.internal.enabled,
            ttl=self.internal.ttl,
            prio=self.internal.priority,
            auth=1).delete()
        if delete_count == 1:
            return ProviderResult.SUCCESS
        return ProviderResult.OTHER_ERROR


class PowerDNSRecordTranslator(ProviderObjectTranslator[CompatDNSRecord]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: CompatDNSRecord) -> Generator[PowerDNSRecordObject, None, None]:
        """Convert Record to PDNS Record"""
        yield PowerDNSRecordObject(
            translator=self,
            internal=internal
        )
