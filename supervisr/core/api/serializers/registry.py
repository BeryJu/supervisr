"""supervisr core api serializers"""
from calendar import timegm
from datetime import date, datetime, timedelta
from inspect import getmro
from typing import Any, Generic, Type, TypeVar, Union
from uuid import UUID

from django.db.models import Model

from supervisr.core.models import CastableModel

# pylint: disable=invalid-name
T = TypeVar('T')

class Serializer(Generic[T]):
    """Serializer for model"""

    def serialize(self, instance: T, parent: 'SerializerRegistry') -> dict:
        """Serialize instance to dict"""
        raise NotImplementedError()


class SerializerRegistry:
    """Holds a registry of all serializers known"""

    __mapping = None
    enable_annotations = None

    def __init__(self):
        self.__mapping = {}
        self.enable_annotations = True

    def annotate(self, value: Any, field_type: Type) -> Union[dict, Any]:
        """Annotate field with a type marking for rendering in frontend"""
        if not self.enable_annotations:
            return value
        if field_type == UUID:
            return {
                '__value': str(value),
                'type': 'uuid'
            }
        if field_type in [date, datetime]:
            return {
                '__value': timegm(value.timetuple()),
                'type': 'timestamp'
            }
        if field_type == timedelta:
            return {
                '__value': value.total_seconds(),
                'type': 'timedelta'
            }
        return value

    def register(self, model: Model, serializer: Serializer):
        """Register a Serializer"""
        self.__mapping[model] = serializer

    def __flatten(self, raw) -> dict:
        """Flatten values from `self.annotate`"""
        flat = {}
        for key, value in raw.items():
            if isinstance(value, dict) and '__value' in value:
                flat[key] = value.pop('__value')
                # Add all sub items to flat, but with key prefix
                for _key, _value in value.items():
                    flat['%s__%s' % (key, _key)] = _value
            else:
                flat[key] = value
        return flat

    def render(self, model_instance: Model) -> dict:
        """Render model while auto-resolving ForeignKeys and ManyToManyFields"""
        serialized = {}
        if isinstance(model_instance, CastableModel):
            model_instance = model_instance.cast()
        # First check model's superclasses and check if those are registered
        # getmro also returns the class of model_instance so we don't need to check that extra
        for superclass in getmro(model_instance.__class__):
            if superclass in self.__mapping:
                serialized.update(self.__mapping.get(superclass).serialize(model_instance, self))
        serialized = self.__flatten(serialized)
        if serialized == {}:
            raise KeyError("No compatible serializers for %s found" % model_instance.__class__)
        return serialized


REGISTRY = SerializerRegistry()

# from supervisr.core.models import Domain
# from supervisr.core.api.serializers.registry import *
# from supervisr.core.api.serializers.domain import *
# from pprint import pprint
# pprint(REGISTRY.render(Domain.objects.first()))
