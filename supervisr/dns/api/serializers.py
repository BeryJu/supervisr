"""supervisr dns serializers"""

from supervisr.core.api.serializers.registry import (REGISTRY, Serializer,
                                                     SerializerRegistry)
from supervisr.dns.models import DataRecord, ReverseZone, SetRecord, Zone

@REGISTRY.serializer(Zone)
class ZoneSerializer(Serializer[Zone]):
    """Serialize Zone"""

    # pylint: disable=unused-argument
    def serialize(self, instance: Zone, parent: SerializerRegistry) -> dict:
        """Serialize Zone"""
        return {
            'domain': parent.render(instance.domain),
        }
