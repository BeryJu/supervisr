"""
Supervisr Core init
"""

from __future__ import print_function
from .errors import PrintUsedException
import builtins

# pylint: disable=unused-argument
def c_print(*args, **kwargs):
    """
    Custom print function which errors out
    """
    raise PrintUsedException("Print is globally disabled in supervisr. "
                             "Please use LOGGER.info for debugging")

builtins.print = c_print
