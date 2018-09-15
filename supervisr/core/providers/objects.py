"""supervisr core provider ObjectMarshall"""
from typing import Generator, Generic, TypeVar

from aenum import IntFlag

T = TypeVar('T')


class ProviderAction(IntFlag):
    """Actions which can be triggered by signals"""

    SAVE = 1
    DELETE = 2


class ProviderResult(IntFlag):
    """All Possible provider results"""

    SUCCESS = 1
    SUCCESS_CREATED = 2
    SUCCESS_UPDATED = 4
    EXISTS_ALREADY = 8
    NOT_SUPPORTED = 16
    NOT_IMPLEMENTED = 32
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

    # pylint: disable=unused-argument
    def save(self, created: bool) -> ProviderResult:
        """Save this instance to provider. Should return True if a new object was saved
        and False if an existing object was modified

        Args:
            created (bool): True if object was freshly created, otherwise False

        Returns:
            ProviderResult: Result of operation
        """
        return ProviderResult.NOT_IMPLEMENTED

    def delete(self) -> ProviderResult:
        """Delete this instance from provider

        Returns:
            ProviderResult: Result of operation
        """
        return ProviderResult.NOT_IMPLEMENTED


class ProviderObjectTranslator(Generic[T]):
    """Gather all methods related to a certain object in context of a Provider

    Args:
        Generic ([type]): Type of internal Object to be translated
    """

    provider_instance = None

    def __init__(self, provider_instance):
        super(ProviderObjectTranslator, self).__init__()
        self.provider_instance = provider_instance

    def to_external(self, internal: T) -> Generator[ProviderObject, None, None]:
        """This function is called when the internal Object should be converted to an instance
        of ProviderObject

        Args:
            internal (T): Instance of internal Model of Type T

        Returns:
            Generator[ProviderObject, None, None]: Yield ProviderObject instances
        """
        raise NotImplementedError()

    # def query_external(self, **kwargs) -> Generator[ProviderObject, None, None]:
    #     """Query external Provider with **kwargs"""
    #     raise NotImplementedError()

    # def to_internal(self, query_result: ProviderObject) -> T:
    #     """Convert external object to T"""
    #     raise NotImplementedError()
