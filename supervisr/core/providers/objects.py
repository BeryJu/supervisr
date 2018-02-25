"""supervisr core provider ObjectMarshall"""
from typing import Generic, List, TypeVar

from supervisr.core.providers.commit import ProviderCommitChange

T = TypeVar('T')

class ProviderObjectMarshall(Generic[T]):
    """Gather all methods related to a certain object in context of a Provider"""

    provider_instance = None

    def __init__(self, provider_instance):
        super(ProviderObjectMarshall, self).__init__()
        self.provider_instance = provider_instance

    def create(self, instance: T) -> bool:
        """Create instance of Object with instance"""
        raise NotImplementedError()

    def has(self, **filters) -> bool:
        """Check if Object matching from key-value filters from **filters exists"""
        raise NotImplementedError()

    def read(self, **filters) -> List[T]:
        """Return List of Object matching key-value filters from **filters"""
        raise NotImplementedError()

    def update(self, instance: T) -> bool:
        """Write updated instance"""
        raise NotImplementedError()

    def delete(self, instance: T) -> bool:
        """Delete instance"""
        raise NotImplementedError()

    def save(self, commit=False) -> List[ProviderCommitChange]:
        """Save changes if commit=True"""
        raise NotImplementedError()
