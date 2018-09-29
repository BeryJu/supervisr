"""supervisr core domain serializer"""
from uuid import UUID

from supervisr.core.api.serializers.registry import (REGISTRY, Serializer,
                                                     SerializerRegistry)
from supervisr.core.models import (BaseCredential, ProviderAcquirableSingle,
                                   ProviderInstance, UUIDModel)


class UUIDModelSerializer(Serializer[UUIDModel]):
    """Serialize UUIDModel"""

    def serialize(self, instance: UUIDModel, parent: SerializerRegistry) -> dict:
        """Serialize UUID"""
        return {
            'uuid': parent.annotate(instance.uuid, UUID),
        }

class CredentialSerializer(Serializer[BaseCredential]):
    """Serialize CredentialModel"""

    def serialize(self, instance: BaseCredential, parent: SerializerRegistry) -> dict:
        """Serialize CredentialModel"""
        return {
            'name': instance.name,
            'owner': parent.render(instance.owner)
        }

class ProviderInstanceSerializer(Serializer[ProviderInstance]):
    """Serialize ProviderInstance"""

    def serialize(self, instance: ProviderInstance, parent: SerializerRegistry) -> dict:
        """Serialize ProviderInstance"""
        return {
            'name': instance.name,
            'provider_path': instance.provider_path,
            'credentials': parent.render(instance.credentials)
        }

class ProviderAcquirableSingleSerializer(Serializer[ProviderAcquirableSingle]):
    """Serialize ProviderAcquirableSingle"""

    def serialize(self, instance: ProviderAcquirableSingle, parent: SerializerRegistry) -> dict:
        """Serialize ProviderAcquirableSingle"""
        return {
            'provider_instance': parent.render(instance.provider_instance),
        }


REGISTRY.register(ProviderAcquirableSingle, ProviderAcquirableSingleSerializer())
REGISTRY.register(ProviderInstance, ProviderInstanceSerializer())
REGISTRY.register(UUIDModel, UUIDModelSerializer())
REGISTRY.register(BaseCredential, CredentialSerializer())
