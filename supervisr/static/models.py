"""supervisr Static Models"""

import logging
import os

from django.conf import settings
from django.db import models

from supervisr.core.models import (CastableModel, CreatedUpdatedModel, Product,
                                   UUIDModel)

LOGGER = logging.getLogger(__name__)


class StaticPage(UUIDModel, CreatedUpdatedModel, CastableModel):
    """Store static page"""
    content = models.TextField()
    template = models.TextField(default='static/generic.html')
    title = models.TextField()
    slug = models.SlugField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    listed = models.BooleanField(default=True)
    views = models.BigIntegerField(default=0)
    has_markdown_enabled = models.BooleanField(default=True)
    has_html_enabled = models.BooleanField(default=True)
    language = models.CharField(max_length=7, default='en')

    def __str__(self):
        return "StaticPage %s (slug=%s)" % (self.title, self.slug)

    class Meta:
        unique_together = (('slug', 'language',),)


class FilePage(StaticPage):
    """Store static page, which is read from file on start"""
    path = models.TextField()

    def update_from_file(self):
        """Read data from file and write to DB"""
        if not os.path.isabs(self.path) and not os.path.exists(self.path):
            # Path is not absolute and file doesnt exist.
            # join with settings.BASE_DIR
            self.path = os.path.join(settings.BASE_DIR, self.path)
        try:
            with open(self.path, mode='r', encoding='utf8') as file:
                new_content = file.read()
                if new_content != self.content:
                    self.content = new_content
                    self.save()
                    return True
                return False
        except IOError:
            LOGGER.error("Failed to read file %s", self.path)

    def __str__(self):
        return "FilePage %s (slug=%s, path=%s)" % (self.title, self.slug, self.path)


class ProductPage(StaticPage):
    """A Page specific for a product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return "ProductPage %s (slug=%s, product=%s)" % (self.title, self.slug, self.product)
