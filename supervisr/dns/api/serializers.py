"""supervisr dns serializers"""

from supervisr.core.api.serializers.registry import (REGISTRY, Serializer,
                                                     SerializerRegistry)
from supervisr.dns.models import ReverseZone, Zone


@REGISTRY.serializer(Zone)
class ZoneSerializer(Serializer[Zone]):
    """Serialize Zone"""

    def serialize(self, instance: Zone, parent: SerializerRegistry) -> dict:
        """Serialize Zone"""
        return {
            'domain': parent.render(instance.domain),
            'enabled': instance.enabled,
        }


@REGISTRY.serializer(ReverseZone)
class ReverseZoneSerializer(Serializer[ReverseZone]):
    """Serialize ReverseZone"""

    # pylint: disable=unused-argument
    def serialize(self, instance: ReverseZone, parent: SerializerRegistry) -> dict:
        """Serialize ReverseZone"""
        return {
            'zone_ip': instance.zone_ip,
            'netmask': instance.netmask,
            'enabled': instance.enabled,
        }
