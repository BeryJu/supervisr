"""
Supervisr Server Generic Provider
"""

import json
from abc import ABCMeta, abstractmethod

import request


class GenericProvider(object):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    __metaclass__ = ABCMeta

    base_url = None
