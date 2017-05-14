"""
Supervisr Core test utils
"""

from io import StringIO

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.cached_db import SessionStore
from django.core.management import call_command
from django.test import RequestFactory


# pylint: disable=too-many-arguments
def test_request(view,
                 method='GET',
                 user=AnonymousUser,
                 session_data=None,
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

    factory_handler = getattr(factory, method.lower(), None)

    if not factory_handler:
        return

    req = factory_handler(view, req_kwargs)

    session = SessionStore()
    if session_data:
        for key, value in session_data.items():
            session[key] = value
    # Fix django.contrib.messages.api.MessageFailure
    # because this request doesn't have a session or anything
    setattr(req, 'session', session)
    setattr(req, '_messages', FallbackStorage(req))

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
