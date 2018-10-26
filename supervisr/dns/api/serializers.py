"""supervisr dns serializers"""

from supervisr.core.api.serializers.registry import (REGISTRY, Serializer,
                                                     SerializerRegistry)
from supervisr.dns.models import DataRecord, ReverseZone, SetRecord, Zone


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


@REGISTRY.serializer(DataRecord)
class DataRecordSerializer(Serializer[DataRecord]):
    """Serialize DataRecord"""

    # pylint: disable=unused-argument
    def serialize(self, instance: DataRecord, parent: SerializerRegistry) -> dict:
        """Serialize DataRecord"""
        return {
            'name': instance.name,
            'enabled': instance.enabled,
            'type': instance.type,
            'content': instance.content,
            'ttl': instance.ttl,
            'priority': instance.priority,
        }


@REGISTRY.serializer(SetRecord)
class SetRecordSerializer(Serializer[SetRecord]):
    """Serialize SetRecord"""

    # pylint: disable=unused-argument
    def serialize(self, instance: SetRecord, parent: SerializerRegistry) -> dict:
        """Serialize SetRecord"""
        return {
            'name': instance.name,
            'enabled': instance.enabled,
            'append_name': instance.append_name,
            'records': [parent.render(record) for record in instance.records],
        }
