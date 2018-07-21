"""Oauth2 provider product extension"""

from django.db import models
from oauth2_provider.models import Application

from supervisr.core.models import ProductExtension


class ProductExtensionOAuth2(ProductExtension):
    """Associate an OAuth2 Application with a Product"""

    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    def __str__(self):
        return "ProductExtension OAuth %s" % self.application.name
