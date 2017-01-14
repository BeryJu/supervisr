"""
Supervisr Core test utils
"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse


def test_request(view,
                 method='GET',
                 user=AnonymousUser,
                 url_kwargs=None,
                 req_kwargs=None):
    """
    Wrapper to make test requests easier
    """

    if url_kwargs is None:
        url_kwargs = {}
    if req_kwargs is None:
        req_kwargs = {}

    factory = RequestFactory()
    if method == 'GET':
        req = factory.get(reverse(view), req_kwargs)
    elif method == 'POST':
        req = factory.post(reverse(view), req_kwargs)

    if user is AnonymousUser:
        user = AnonymousUser()
    elif isinstance(user, int):
        user = User.objects.get(pk=user)
    req.user = user

    return view(req, **url_kwargs)
