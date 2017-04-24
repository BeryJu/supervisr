"""
Supervisr Core Generic Provider
"""

from abc import ABCMeta


class BaseProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    __metaclass__ = ABCMeta

    base_url = None
