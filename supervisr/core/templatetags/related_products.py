"""
Supervisr Core related_products
"""
from django import template

from supervisr.core.models import Product
from supervisr.core.utils import path_to_class

register = template.Library()

@register.simple_tag(takes_context=True)
def related_products(context, product_path):
    """
    Return list of products which have a UPR to current user
    """
    request = context.get('request', None)
    if not request:
        # No Request -> no user -> return empty
        return []
    user = request.user

    model = path_to_class(product_path)
    if not issubclass(model, Product):
        # product_path is not actually a module
        # so we can't assume that it's usable
        return []

    return model.objects.filter(users__in=[user])
