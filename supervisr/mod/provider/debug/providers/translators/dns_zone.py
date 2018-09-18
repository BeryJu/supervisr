"""supervisr mod provider Debug Zone Translator"""
from logging import getLogger
from typing import Generator

from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)
from supervisr.dns.models import Zone

LOGGER = getLogger(__name__)


class DebugZoneObject(ProviderObject):
    """Debug Zone Object"""

    def save(self) -> ProviderResult:
        LOGGER.debug("Instance %s saved", self.name)
        return ProviderResult.SUCCESS

    def delete(self) -> ProviderResult:
        LOGGER.debug("Instance %s deleted", self.name)
        return ProviderResult.SUCCESS


class DebugZoneTranslator(ProviderObjectTranslator[Zone]):
    """Debug Zone Translator"""

    def to_external(self, internal: Zone) -> Generator[DebugZoneObject, None, None]:
        """Create DebugZoneObject from Zone"""
        LOGGER.debug("to_external %r", internal)
        yield DebugZoneObject(
            translator=self,
            name=internal.domain.domain_name
        )
