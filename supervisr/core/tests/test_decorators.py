"""Supervisr Core Decorator Test"""

import time

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from supervisr.core.decorators import (RE_AUTH_KEY, RE_AUTH_MARGAIN, ifapp,
                                       logged_in_or_basicauth, reauth_required,
                                       require_setting)
from supervisr.core.models import Setting
from supervisr.core.utils import b64encode
from supervisr.core.utils.tests import TestCase, test_request
from supervisr.core.views import accounts, common


class TestDecorators(TestCase):
    """Supervisr Core Decorator Test"""

    def setUp(self):
        super(TestDecorators, self).setUp()
        Setting.set('analytics:ga:enabled', True)

    def test_anonymous_required(self):
        """Test anonymous_required decorator"""
        # View as AnonymousUser should return 200
        self.assertEqual(test_request(accounts.LoginView.as_view(),
                                      user=AnonymousUser()).status_code, 200)
        # As logged in user should redirect to index
        self.assertEqual(test_request(accounts.LoginView.as_view(),
                                      user=self.system_user).status_code, 302)

    def test_reauth_required(self):
        """Test reauth_required decorator"""
        # View as AnonymousUser should return 302
        self.assertEqual(test_request(reauth_required(common.IndexView.as_view()),
                                      user=AnonymousUser()).status_code, 302)
        self.assertEqual(test_request(reauth_required(common.IndexView.as_view()),
                                      user=self.system_user).status_code, 302)
        # Test reauth with valid time
        self.assertEqual(
            test_request(reauth_required(common.IndexView.as_view()),
                         user=self.system_user,
                         session_data={RE_AUTH_KEY: time.time()}).status_code, 200)
        # Test reauth with old time time
        self.assertEqual(
            test_request(reauth_required(common.IndexView.as_view()),
                         user=self.system_user,
                         session_data={RE_AUTH_KEY: time.time() - RE_AUTH_MARGAIN - 100})
            .status_code, 302)

    def test_ifapp(self):
        """Test ifapp decorator"""
        @ifapp('supervisr_core')
        def test_core():
            """Only run this function if app core is present"""
            return True

        @ifapp('_invalid-name')
        def test_invalid():
            """Only run this function if app '_invalid-name' is present"""
            pass  # pragma: no cover

        self.assertTrue(test_core())
        self.assertEqual(test_invalid(), False)

    def test_basic_auth(self):
        """test http basic auth"""
        @logged_in_or_basicauth(realm='testrealm')
        def _view(request):
            """ user has gotten through so everything's fine """
            return HttpResponse(status=204)

        self.system_user.is_active = True
        self.system_user.set_password('temppw')
        self.system_user.save()

        headers = {
            'HTTP_AUTHORIZATION': 'Basic %s' % b64encode('%s:%s' % (self.system_user.email,
                                                                    'temppw'))
        }

        # Test already logged in
        self.assertEqual(test_request(_view, user=self.system_user).status_code, 204)
        # Test header
        self.assertEqual(test_request(_view, headers=headers).status_code, 204)
        # Test nothing
        res_401 = test_request(_view)
        self.assertEqual(res_401.status_code, 401)
        self.assertIn('www-authenticate', res_401)
        self.assertIn('testrealm', res_401['www-authenticate'])

    def test_require_setting(self):
        """Test require_setting decorator"""
        @require_setting('supervisr.core/test', True)
        def view(request):
            """dummy view"""
            return HttpResponse('success')

        # test with setting enabled, should return 'success'
        Setting.set('test', True, namespace='supervisr.core')
        self.assertEqual(test_request(view).content.decode('utf-8'), 'success')

        # test with setting disabled
        Setting.set('test', False, namespace='supervisr.core')
        self.assertNotEqual(test_request(view).content.decode('utf-8'), 'success')
