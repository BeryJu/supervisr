"""
Supervisr Mod 2FA Middleware Test
"""

import os

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.views import common
from supervisr.mod.tfa.middleware import tfa_force_verify


class TestMiddleware(TestCase):
    """
    Supervisr 2FA Middleware Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_tfa_force_verify_anon(self):
        """
        Test Anonymous TFA Force
        """
        req = self.factory.get(reverse('common-index'))
        req.user = AnonymousUser()
        res = tfa_force_verify(common.index)(req)
        self.assertEqual(res.status_code, 302)
