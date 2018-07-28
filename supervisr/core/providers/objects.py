"""supervisr core provider ObjectMarshall"""
from enum import IntEnum
from typing import Generic, List, TypeVar

T = TypeVar('T')


class ProviderrResult(IntEnum):
    """All Possible provider results"""

    SUCCESS = 0
    EXISTS_ALREADY = 1
    NOT_SUPPORTED = 2
    NOT_IMPLEMENTED = 4
    OTHER_ERROR = 1024


class ProviderObject(object):
    """This class defines properties that should be returned from queries.

    Custom fields can be added in subclasses"""

    id = None
    name = None
    translator = None

    def __init__(self, translator: 'ProviderObjectTranslator', **kwargs):
        self.translator = translator
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self) -> ProviderrResult:
        """Save this instance to provider. Should return True if a new object was saved
        and False if an existing object was modified"""
        return ProviderrResult.NOT_IMPLEMENTED

    def delete(self) -> ProviderrResult:
        """Delete this instance from provider"""
        return ProviderrResult.NOT_IMPLEMENTED


class ProviderObjectTranslator(Generic[T]):
    """Gather all methods related to a certain object in context of a Provider"""

    provider_instance = None

    def __init__(self, provider_instance):
        super(ProviderObjectTranslator, self).__init__()
        self.provider_instance = provider_instance

    def to_external(self, internal: T) -> ProviderObject:
        """Convert instance of T to external object"""
        raise NotImplementedError()

    def query_external(self, **kwargs) -> List[ProviderObject]:
        """Query external Provider with **kwargs"""
        raise NotImplementedError()

    def to_internal(self, query_result: ProviderObject) -> T:
        """Convert external object to T"""
        raise NotImplementedError()
