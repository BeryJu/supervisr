"""
Supervisr Core init
"""

from __future__ import print_function
from .errors import PrintUsedException

# pylint: disable=unused-argument, redefined-builtin
def print(*args, **kwargs):
    """
    Custom print function which errors out
    """
    raise PrintUsedException()
