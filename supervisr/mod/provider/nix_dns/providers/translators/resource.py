"""supervisr mod provider PowerDNS Resource Translator"""
from typing import Generator

from supervisr.core.providers.objects import ProviderObjectTranslator
from supervisr.dns.models import Resource
from supervisr.mod.provider.nix_dns.providers.translators.record import \
    PowerDNSRecordTranslator


class PowerDNSResourceTranslator(ProviderObjectTranslator[Resource]):
    """PowerDNS Zone Translator"""

    def to_external(self, internal: Resource) -> Generator[PowerDNSRecordTranslator, None, None]:
        """Trigger Record update from resource"""
        for resource_set in internal.resourceset_set.all():
            for record in resource_set:
                yield PowerDNSRecordTranslator(
                    translator=self,
                    internal=record
                )
