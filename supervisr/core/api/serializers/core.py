"""supervisr core domain serializer"""
from datetime import datetime, timedelta
from uuid import UUID

from django.utils import timezone

from supervisr.core.api.serializers.registry import (REGISTRY, LinkType,
                                                     Serializer,
                                                     SerializerRegistry)
from supervisr.core.models import (Domain, Event, ProviderAcquirable, User,
                                   UserAcquirable)


@REGISTRY.serializer(User)
class UserSerializer(Serializer[User]):
    """Serialize User"""

    # pylint: disable=unused-argument
    def serialize(self, instance: User, parent: SerializerRegistry) -> dict:
        """Serialize User"""
        serialized = {
            'short_name': instance.short_name,
        }
        if self.is_superuser and self.root_model == User:
            # User is superuser and we're root -> send more data
            serialized['email'] = instance.email
            serialized['username'] = instance.username
            serialized['date_joined'] = parent.annotate(instance.date_joined, datetime)
            serialized['impersonate'] = parent.annotate('?__impersonate=%s' % instance.pk, LinkType)
        return serialized


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


@REGISTRY.serializer(ProviderAcquirable)
class ProviderAcquirableSerializer(Serializer[ProviderAcquirable]):
    """Serialize ProviderAcquirable"""

    # pylint: disable=unused-argument
    def serialize(self, instance: ProviderAcquirable, parent: SerializerRegistry) -> dict:
        """Serialize ProviderAcquirable"""
        return {
            'providers': {
                provider.name: provider.uuid for provider in instance.providers.all()
            }
        }


@REGISTRY.serializer(UserAcquirable)
class UserAcquirableSerializer(Serializer[UserAcquirable]):
    """Serialize UserAcquirable"""

    def serialize(self, instance: UserAcquirable, parent: SerializerRegistry) -> dict:
        """Serialize UserAcquirable"""
        return {
            'users': {
                user.username: parent.render(user) for user in instance.users.all()
            }
        }
