"""
Supervisr Core test utils
"""

from io import StringIO

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.management import call_command
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

    # Fix django.contrib.messages.api.MessageFailure
    # because this request doesn't have a session or anything
    setattr(req, 'session', 'session')
    messages = FallbackStorage(req)
    setattr(req, '_messages', messages)

    if user is AnonymousUser:
        user = AnonymousUser()
    elif isinstance(user, int):
        user = User.objects.get(pk=user)
    req.user = user

    return view(req, **url_kwargs)

def call_command_ret(*args, **kwargs):
    """
    This is a wrapper for django's call_command, but it returns the stdout output
    """
    with StringIO() as output:
        call_command(*args, stdout=output, stderr=output, **kwargs)
        return output.getvalue()
