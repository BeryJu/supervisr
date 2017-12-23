"""
Supervisr Foreman Provider Models
"""

from django.db import models

from supervisr.core.models import UserPasswordCredential


class UserPasswordServerCredential(UserPasswordCredential):
    """
    UserPasswordCredential which also holds a server
    """

    server = models.CharField(max_length=255)
