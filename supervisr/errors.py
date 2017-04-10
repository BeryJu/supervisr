"""
Supervisr Core Errors
"""


class SignalException(Exception):
    """
    Exception which is used as a base for all Exceptions in Signals
    """
    pass

class PrintUsedException(Exception):
    """
    Exception which is used when print is used
    """
    pass
