"""
supervisr view decorators
"""

from django.shortcuts import redirect
from django.urls import reverse


def anonymous_required(view_function):
    """
    Wrapper for class-based AnonymousRequired
    """
    return AnonymousRequired(view_function)

# pylint: disable=too-few-public-methods
class AnonymousRequired(object):
    """
    Decorator to only allow a view for anonymous users
    """

    def __init__(self, view_function):
        self.view_function = view_function

    def __call__(self, req, *args, **kwargs):
        if req.user is not None and req.user.is_authenticated():
            return redirect(reverse('common-index'))
        return self.view_function(req, *args, **kwargs)
