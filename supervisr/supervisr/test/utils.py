import os
from unittest import skip

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from ..controllers import AccountController
from ..forms.account import *
from ..ldap_connector import LDAPConnector
from ..models import *
from ..views import account

def test_request(view,
    method='GET',
    user=AnonymousUser,
    url_kwargs={},
    req_kwargs={}):

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
