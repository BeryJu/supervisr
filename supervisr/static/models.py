"""
Supervisr Static Models
"""

from django.contrib.auth.models import User
from django.db import models

from supervisr.core.models import CastableModel, CreatedUpdatedModel


class StaticPage(CreatedUpdatedModel, CastableModel):
    """
    Store static page
    """
    content = models.TextField()
    template = models.TextField(default='static/generic.html')
    title = models.TextField()
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User)
    published = models.BooleanField(default=False)
    listed = models.BooleanField(default=True)
    views = models.BigIntegerField(default=0)
    has_markdown_enabled = models.BooleanField(default=True)
    has_html_enabled = models.BooleanField(default=True)

    def __str__(self):
        return "StaticPage %s (slug=%s)" % (self.title, self.slug)

class FilePage(StaticPage):
    """
    Stora static page, which is read from file on start
    """
    path = models.TextField()

    def update_from_file(self):
        """
        Read data from file and write to DB
        """
        with open(self.path, 'r') as file:
            self.content = file.read()
            self.save()

    def __str__(self):
        return "FilePage %s (slug=%s, path=%s)" % (self.title, self.slug, self.path)
