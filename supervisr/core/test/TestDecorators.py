"""
Supervisr Core Decorator Test
"""

import os
import time

from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from django.test import TestCase

from supervisr.core.decorators import (REAUTH_KEY, REAUTH_MARGIN, ifapp,
                                       logged_in_or_basicauth, reauth_required)
from supervisr.core.models import Setting, get_system_user
from supervisr.core.test.utils import test_request
from supervisr.core.utils import b64encode
from supervisr.core.views import accounts, common


class TestDecorators(TestCase):
    """
    Supervisr Core Decorator Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        Setting.set('analytics:ga:enabled', True)

    def test_anonymous_required(self):
        """
        Test anonymous_required decorator
        """
        # View as AnonymousUser should return 200
        self.assertEqual(test_request(accounts.LoginView.as_view(),
                                      user=AnonymousUser()).status_code, 200)
        # As logged in user should redirect to index
        self.assertEqual(test_request(accounts.LoginView.as_view(),
                                      user=get_system_user()).status_code, 302)

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
            pass # pragma: no cover

        self.assertTrue(test_core())
        self.assertEqual(test_invalid(), None)

    def test_basic_auth(self):
        """
        test http basic auth
        """
        @logged_in_or_basicauth(realm='testrealm')
        # pylint: disable=unused-argument
        def _view(request):
            """
            user has gotten through so everything's fine
            """
            return HttpResponse(status=204)

        user = User.objects.get(pk=get_system_user())
        user.is_active = True
        user.set_password('temppw')
        user.save()

        headers = {
            'HTTP_AUTHORIZATION': 'Basic %s' % b64encode(':'.join([user.username, 'temppw']))
        }

        # Test already logged in
        self.assertEqual(test_request(_view, user=user).status_code, 204)
        # Test header
        self.assertEqual(test_request(_view, headers=headers).status_code, 204)
        # Test nothing
        res_401 = test_request(_view)
        self.assertEqual(res_401.status_code, 401)
        self.assertIn('www-authenticate', res_401)
        self.assertIn('testrealm', res_401['www-authenticate'])
