"""supervisr core provider exceptions"""

from supervisr.core.exceptions import SupervisrException


class SupervisrProviderException(SupervisrException):
    """Base Exception for all provider exceptions"""
    pass


class ProviderObjectNotFoundException(SupervisrProviderException):
    """Exception if an object could not be found"""
    pass


class ProviderRetryException(SupervisrProviderException):
    """Exception which triggers retries. Should be used when a provider experiences
    a temporary service outage."""
    pass
