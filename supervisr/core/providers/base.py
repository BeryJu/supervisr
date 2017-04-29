"""
Supervisr Core Generic Provider
"""

from django.db import models
from django.contrib.auth.models import User


class BaseProvider(models.Model):
    """
    Generic Interface as base for GenericManagedProvider and GenericUserProvider
    """

    setup_form = []

    class Meta:
        abstract = True

class BaseProviderInstance(models.Model):
    """
    Save information about information specifially for a user
    """

    provider = models.ForeignKey(BaseProvider)
    user = models.ForeignKey(User)
