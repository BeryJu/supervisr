"""supervisr mod provider Debug Domain Translator"""
from logging import getLogger
from typing import Generator

from supervisr.core.models import Domain
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator,
                                              ProviderResult)

LOGGER = getLogger(__name__)


class DebugDomainObject(ProviderObject):
    """Debug Domain Object"""

    def save(self, created: bool) -> ProviderResult:
        LOGGER.debug("Instance %s saved (created=%r)", self.name, created)
        return ProviderResult.SUCCESS

    def delete(self) -> ProviderResult:
        LOGGER.debug("Instance %s deleted", self.name)
        return ProviderResult.SUCCESS


class DebugDomainTranslator(ProviderObjectTranslator[Domain]):
    """Debug Domain Translator"""

    def to_external(self, internal: Domain) -> Generator[DebugDomainObject, None, None]:
        """Create DebugDomainObject from Domain"""
        LOGGER.debug("to_external %r", internal)
        yield DebugDomainObject(
            translator=self,
            name=internal.domain_name
        )
