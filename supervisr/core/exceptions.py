"""Supervisr Core Errors"""


class SupervisrException(Exception):
    """Base Exception class for all supervisr exceptions"""
    pass


class SignalException(SupervisrException):
    """Exception which is used as a base for all Exceptions in Signals"""
    pass


class UnauthorizedExcception(SupervisrException):
    """User is not authorized"""
    pass
