"""supervisr mod provider Debug Domain Translator"""
from logging import getLogger
from typing import List

from supervisr.core.models import Domain
from supervisr.core.providers.exceptions import ProviderObjectNotFoundException
from supervisr.core.providers.objects import (ProviderObject,
                                              ProviderObjectTranslator)

LOGGER = getLogger(__name__)

class DebugDomainObject(ProviderObject):
    """Debug Domain Object"""

    def save(self) -> bool:
        LOGGER.debug("Instance %s saved", self.name)
        return True

    def delete(self):
        LOGGER.debug("Instance %s deleted", self.name)

class DebugDomainTranslator(ProviderObjectTranslator[Domain]):
    """Debug Domain Translator"""

    def to_external(self, internal: Domain) -> DebugDomainObject:
        """Create DebugDomainObject from Domain"""
        LOGGER.debug("to_external %r", internal)
        return DebugDomainObject(
            translator=self,
            name=internal.domain_name
        )

    def query_external(self, **kwargs) -> List[DebugDomainObject]:
        """Query DebugDomainObjects. Since these are used for debugging and not saved,
        return an empty array"""
        LOGGER.debug("query %r", kwargs)
        return []

    def to_internal(self, query_result: DebugDomainObject) -> Domain:
        """Convert DebugDomainObject to Domain"""
        domains = Domain.objects.filter(domain_name=query_result.name)
        if not domains.exists():
            raise ProviderObjectNotFoundException()
        assert len(domains) == 1
        return domains.first()
