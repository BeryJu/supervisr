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

    is_superuser = False
    root_model = Model

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def serialize(self, instance: T, parent: 'SerializerRegistry') -> dict:
        """Serialize instance to dict"""
        raise NotImplementedError()


class LinkType:
    """Stub class to annotate a Link"""


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
        if field_type == LinkType:
            return {
                '__value': value,
                'type': 'link'
            }
        return value

    def serializer(self, model: Model):
        """Class decorator to register classes inline."""
        def inner_wrapper(cls):
            self.__mapping[model] = cls
            return cls
        return inner_wrapper

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

    def render(self, model_instance: Model, **extra) -> dict:
        """Render model while auto-resolving ForeignKeys and ManyToManyFields"""
        serialized = {}
        if isinstance(model_instance, CastableModel):
            model_instance = model_instance.cast()
        # First check model's superclasses and check if those are registered
        # getmro also returns the class of model_instance so we don't need to check that extra
        for superclass in getmro(model_instance.__class__):
            if superclass in self.__mapping:
                serializer_class = self.__mapping.get(superclass)
                serializer_instance = serializer_class(**extra)
                serialized.update(serializer_instance.serialize(model_instance, self))
        serialized = self.__flatten(serialized)
        if serialized == {}:
            raise KeyError("No compatible serializers for %s found" % model_instance.__class__)
        return serialized


REGISTRY = SerializerRegistry()
