"""supervisr core domain serializer"""
from datetime import timedelta
from uuid import UUID

from django.utils import timezone

from supervisr.core.api.serializers.registry import (REGISTRY, Serializer,
                                                     SerializerRegistry)
from supervisr.core.models import Domain, Event, User


@REGISTRY.serializer(User)
class UserSerializer(Serializer[User]):
    """Serialize User"""

    # pylint: disable=unused-argument
    def serialize(self, instance: User, parent: SerializerRegistry) -> dict:
        """Serialize User"""
        return {
            'username': instance.short_name,
        }


@REGISTRY.serializer(Domain)
class DomainSerializer(Serializer[Domain]):
    """Serialize Domain"""

    # pylint: disable=unused-argument
    def serialize(self, instance: Domain, parent: SerializerRegistry) -> dict:
        """Serialize Domain"""
        return {
            'domain_name': instance.domain_name,
            'description': instance.description,
        }


@REGISTRY.serializer(Event)
class EventSerializer(Serializer[Event]):
    """Serialize Event"""

    def serialize(self, instance: Event, parent: SerializerRegistry) -> dict:
        """Serialize Event"""
        return {
            'user': parent.render(instance.user),
            'uuid': parent.annotate(instance.uuid, UUID),
            'message': instance.message,
            'created': parent.annotate(timezone.now() - instance.create_date, timedelta),
        }
