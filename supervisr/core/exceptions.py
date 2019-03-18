"""Supervisr Core Errors"""


class SupervisrException(Exception):
    """Base Exception class for all supervisr exceptions"""


class SignalException(SupervisrException):
    """Exception which is used as a base for all Exceptions in Signals"""


class UnauthorizedException(SupervisrException):
    """User is not authorized"""
