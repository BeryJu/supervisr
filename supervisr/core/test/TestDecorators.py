"""
Supervisr Core Decorator Test
"""


import os
import time

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from ..decorators import REAUTH_KEY, REAUTH_MARGIN, ifapp, reauth_required
from ..models import Setting, get_system_user
from ..views import account, common
from .utils import test_request


class TestDecorators(TestCase):
    """
    Supervisr Core Decorator Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        Setting.set('core:analytics:ga:enabled', True)

    def test_anonymous_required(self):
        """
        Test anonymous_required decorator
        """
        # View as AnonymousUser should return 200
        self.assertEqual(test_request(account.login, user=AnonymousUser()).status_code, 200)
        # As logged in user should redirect to index
        self.assertEqual(test_request(account.login, user=get_system_user()).status_code, 302)

    def test_reauth_required(self):
        """
        Test reauth_required decorator
        """
        # View as AnonymousUser should return 302
        self.assertEqual(test_request(reauth_required(common.index),
                                      user=AnonymousUser()).status_code, 302)
        self.assertEqual(test_request(reauth_required(common.index),
                                      user=get_system_user()).status_code, 302)
        # Test reauth with valid time
        self.assertEqual(test_request(reauth_required(common.index),
                                      user=get_system_user(), session_data={
                                          REAUTH_KEY: time.time()
                                      }).status_code, 200)
        # Test reauth with old time time
        self.assertEqual(test_request(reauth_required(common.index),
                                      user=get_system_user(), session_data={
                                          REAUTH_KEY: time.time() - REAUTH_MARGIN - 100
                                      }).status_code, 302)

    def test_ifapp(self):
        """
        Test ifapp decorator
        """
        @ifapp('core')
        def test_core():
            """
            Only run this function if app core is present
            """
            return True

        @ifapp('_invalid-name')
        def test_invalid():
            """
            Only run this function if app '_invalid-name' is present
            """
            pass

        self.assertTrue(test_core())
        self.assertEqual(test_invalid(), None)
