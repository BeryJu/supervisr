"""supervisr mod provider Debug Zone Marshall"""
from typing import List

from supervisr.core.providers.objects import ProviderObjectMarshall
from supervisr.dns.models import Zone


class DebugZoneMarshall(ProviderObjectMarshall[Zone]):
    """Debug Zone Marshall"""

    def create(self, instance: Zone) -> bool:
        """Create instance of Object with **kwargs"""
        pass

    def has(self, **filters) -> bool:
        """Check if Object matching from key-value filters from **filters exists"""
        raise NotImplementedError()

    def read(self, **filters) -> List[Zone]:
        """Return List of Object matching key-value filters from **filters"""
        pass

    # pylint: disable=unused-argument
    def update(self, instance: Zone) -> bool:
        """Write updated instance"""
        # pdns_instance = Domain.objects.filter(name=instance.domain.domain_name)
        # There is only one field being translated so we can't update
        return True

    def delete(self, instance: Zone) -> bool:
        """Delete instance"""
        pass
