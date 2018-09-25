"""supervisr mod web_proxy Models"""

from django.db import models

from supervisr.core.models import UserAcquirable, UUIDModel


class WebApplication(UUIDModel, UserAcquirable):
    """A webapplication we should proxy for"""

    name = models.TextField()
    upstream = models.URLField()
    access_slug = models.SlugField()
    add_remote_user = models.BooleanField(default=True)

    def __str__(self):
        return "WebApplication %s" % self.name
