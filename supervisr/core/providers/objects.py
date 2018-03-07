"""supervisr core provider ObjectMarshall"""
from typing import Generic, List, TypeVar

T = TypeVar('T')

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

    def save(self) -> bool:
        """Save this instance to provider. Should return True if a new object was saved
        and False if an existing object was modified"""
        raise NotImplementedError()

    def delete(self):
        """Delete this instance from provider"""
        raise NotImplementedError()

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