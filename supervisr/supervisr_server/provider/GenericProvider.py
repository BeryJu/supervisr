"""
Supervisr Server Generic Provider
"""

from abc import ABCMeta


class GenericProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    __metaclass__ = ABCMeta

    base_url = None
