"""
Supervisr Core related_models
"""
from django import template
from supervisr.core.models import UserAcquirable
from supervisr.core.utils import path_to_class

register = template.Library()


@register.simple_tag(takes_context=True)
def related_models(context, model_path):
    """
    Return list of models which have a Relationship to current user
    """
    request = context.get('request', None)
    if not request:
        # No Request -> no user -> return empty
        return []
    user = request.user

    model = path_to_class(model_path)
    if not issubclass(model, UserAcquirable):
        # model_path is not actually a module
        # so we can't assume that it's usable
        return []

    return model.objects.filter(users__in=[user])
