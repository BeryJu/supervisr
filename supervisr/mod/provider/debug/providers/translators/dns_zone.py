"""supervisr mod provider Debug Zone Translator"""
from logging import getLogger
from typing import List

from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator)
from supervisr.dns.models import Zone

LOGGER = getLogger(__name__)


class DebugZoneObject(ProviderObject):
    """Debug Zone Object"""

    def save(self) -> bool:
        LOGGER.debug("Instance %s saved", self.name)
        return True

    def delete(self):
        LOGGER.debug("Instance %s deleted", self.name)


class DebugZoneTranslator(ProviderObjectTranslator[Zone]):
    """Debug Zone Translator"""

    def to_external(self, internal: Zone) -> DebugZoneObject:
        """Create DebugZoneObject from Zone"""
        LOGGER.debug("to_external %r", internal)
        return DebugZoneObject(
            translator=self,
            name=internal.domain.domain_name
        )

    def query_external(self, **kwargs) -> List[DebugZoneObject]:
        """Query DebugZoneObjects. Since these are used for debugging and not saved,
        return an empty array"""
        LOGGER.debug("query %r", kwargs)
        return []

    def to_internal(self, query_result: DebugZoneObject) -> Zone:
        """Convert DebugZoneObject to Zone"""
        zones = Zone.objects.filter(domain__domain_name=query_result.name)
        if not zones.exists():
            raise ProviderObjectNotFoundException()
        return zones.first()
