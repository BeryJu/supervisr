"""Supervisr Core test utils"""

import os
from io import StringIO

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.cached_db import SessionStore
from django.core.management import call_command
from django.http import Http404, HttpResponse
from django.http.response import HttpResponseNotFound, HttpResponseServerError
from django.test import RequestFactory
from django.test import TestCase as DjangoTestCase

from supervisr.core.models import EmptyCredential, ProviderInstance


# pylint: disable=too-many-arguments
def test_request(view: callable,
                 method='GET',
                 user: User = SVAnonymousUser,
                 session_data: dict = None,
                 url_kwargs: dict = None,
                 req_kwargs: dict = None,
                 headers: dict = None,
                 just_request: bool = False) -> HttpResponse:
    """Wrapper to make test requests easier

    Args:
        method (str): Request method. Defaults to GET.
        user (User): Requesting user. Defaults to SVAnonymousUser.
        session_data (dict): Optional dictionary of session data.
        url_kwargs (dict): Optional dictionary of URL arguments.
        req_kwargs (dict): Optional dictionary of URL Querystrinng arguments.
        headers (dict): Optional dictionary of headers.
        just_request (bool): Only return the Request. Defaults to False
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
        return HttpResponseServerError()

    # pylint: disable=not-callable
    request = factory_handler(view, req_kwargs, **headers)

    session = SessionStore()
    if session_data:
        for key, value in session_data.items():
            session[key] = value
    # Fix django.contrib.messages.api.MessageFailure
    # because this request doesn't have a session or anything
    setattr(request, 'session', session)
    setattr(request, '_messages', FallbackStorage(request))

    if user is SVAnonymousUser:
        user = SVAnonymousUser()
    request.user = user

    if just_request:
        return request

    try:
        return view(request, **url_kwargs)
    except Http404:
        return HttpResponseNotFound('not found')
    else:
        return HttpResponseServerError()


def internal_provider(user):
    """Quickly create an instance of internal Provider"""
    credentials, _created = EmptyCredential.objects.get_or_create(
        owner=user,
        name='internal-unittest-%s' % str(user))
    provider, _created = ProviderInstance.objects.get_or_create(
        credentials=credentials,
        provider_path='supervisr.provider.debug.providers.core.DebugProvider')
    return provider, credentials


def call_command_ret(*args, **kwargs):
    """This is a wrapper for django's call_command, but it returns the stdout output"""
    with StringIO() as output:
        call_command(*args, stdout=output, stderr=output, **kwargs)
        return output.getvalue()


class TestCase(DjangoTestCase):
    """Django TestCase Wrapper that automatically fetches System User"""

    def setUp(self):
        self.system_user = get_system_user()
        self.provider, self.credentials = internal_provider(self.system_user)
        os.environ['RECAPTCHA_TESTING'] = 'True'


# def oauth2_get_token(user):
#     """
#     Generate an OAuth2 Token for unittests
#     """
#     app = Application.objects.create(
#         client_type=Application.CLIENT_CONFIDENTIAL,
#         authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
#         redirect_uris='https://supervisr-unittest.beryju.org/oauth2/callback',
#         name='dummy',
#         user=user
#     )
#     access_token = AccessToken.objects.create(
#         user=user,
#         scope='read write',
#         expires=timezone.now() + timedelta(seconds=300),
#         token='secret-access-token-key',
#         application=app
#     )
#     return "Bearer {0}".format(access_token)
