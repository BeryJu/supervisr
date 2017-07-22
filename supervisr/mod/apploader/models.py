"""
Supervisr mod App Loader models
"""

from django.db import models


class DBApp(models.Model):
    """
    Django Application meta info
    """

    name = models.TextField(editable=False)
    path = models.TextField(editable=False)
    enabled = models.BooleanField(default=True)
    forced = models.BooleanField(default=False)

    def __str__(self):
        return "DBApp %s (%s)" % (self.name, self.path)
