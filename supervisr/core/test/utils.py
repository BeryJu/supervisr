"""
Supervisr Core test utils
"""

from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.cached_db import SessionStore
from django.core.management import call_command
from django.http import Http404
from django.http.response import HttpResponseNotFound
from django.test import RequestFactory
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application


# pylint: disable=too-many-arguments
def test_request(view,
                 method='GET',
                 user=AnonymousUser,
                 session_data=None,
                 url_kwargs=None,
                 req_kwargs=None,
                 headers=None,
                 just_request=False):
    """
    Wrapper to make test requests easier
    """

    if url_kwargs is None:
        url_kwargs = {}
    if req_kwargs is None:
        req_kwargs = {}
    if headers is None:
        headers = {}

    factory = RequestFactory()

    factory_handler = getattr(factory, method.lower(), None)

    if not factory_handler:
        return

    # pylint: disable=not-callable
    req = factory_handler(view, req_kwargs, **headers)

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

    if just_request:
        return req

    try:
        return view(req, **url_kwargs)
    except Http404:
        return HttpResponseNotFound('not found')

def call_command_ret(*args, **kwargs):
    """
    This is a wrapper for django's call_command, but it returns the stdout output
    """
    with StringIO() as output:
        call_command(*args, stdout=output, stderr=output, **kwargs)
        return output.getvalue()

def oauth2_get_token(user):
    """
    Generate an OAuth2 Token for unittests
    """
    app = Application.objects.create(
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris='https://supervisr-unittest.beryju.org/oauth2/callback',
        name='dummy',
        user=user
    )
    access_token = AccessToken.objects.create(
        user=user,
        scope='read write',
        expires=timezone.now() + timedelta(seconds=300),
        token='secret-access-token-key',
        application=app
    )
    return "Bearer {0}".format(access_token)
