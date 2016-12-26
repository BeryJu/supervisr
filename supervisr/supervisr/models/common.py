from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _

class Product(object):
    product_id = models.AutoField(primary_key=True)
    name = models.TextField()
    slug = models.TextField()
    price = models.DecimalField()
