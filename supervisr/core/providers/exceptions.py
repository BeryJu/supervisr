"""supervisr core provider exceptions"""

class SupervisrProviderException(Exception):
    """Base Exception for all provider exceptions"""
    pass

class ProviderObjectNotFoundException(SupervisrProviderException):
    """Exception if an object could not be found"""
    pass