"""
Supervisr Namecheap Models
"""

from django.db import models

from supervisr.core.models import BaseCredential


class NamecheapCredentials(BaseCredential):

    api_key = models.TextField()
    api_user = models.TextField()
    username = models.TextField()
    sandbox = models.BooleanField(default=True)

    form = 'supervisr.mod.namecheap.forms.setup.SetupForm'

    @staticmethod
    def type():
        return "Namecheap Credentials"
