"""supervisr mod provider Debug Domain Marshall"""
from typing import List

from supervisr.core.models import Domain
from supervisr.core.providers.objects import ProviderObjectMarshall


class DebugDomainMarshall(ProviderObjectMarshall[Domain]):
    """Debug Domain Marshall"""

    def create(self, instance: Domain) -> bool:
        """Create instance of Object with **kwargs"""
        pass

    def has(self, **filters) -> bool:
        """Check if Object matching from key-value filters from **filters exists"""
        raise NotImplementedError()

    def read(self, **filters) -> List[Domain]:
        """Return List of Object matching key-value filters from **filters"""
        pass

    # pylint: disable=unused-argument
    def update(self, instance: Domain) -> bool:
        """Write updated instance"""
        # pdns_instance = Domain.objects.filter(name=instance.domain.domain_name)
        # There is only one field being translated so we can't update
        return True

    def delete(self, instance: Domain) -> bool:
        """Delete instance"""
        pass
