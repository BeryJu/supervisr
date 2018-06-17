"""Supervisr Core Middleware Test"""

from django.contrib import messages
from django.core.management import call_command
from supervisr.core.middleware.deploy_page_middleware import deploy_page
from supervisr.core.middleware.impersonate_middleware import impersonate
from supervisr.core.middleware.permanent_message_middleware import \
    permanent_message
from supervisr.core.models import Setting, User
from supervisr.core.test.utils import TestCase, test_request
from supervisr.core.views import accounts, common


class TestMiddleware(TestCase):
    """Supervisr Core Middleware Test"""

    def tearDown(self):
        """Clean up"""
        call_command('deploy_page', 'down')

    def test_deploy_page_off(self):
        """Test Disabled Deploy Page"""
        call_command('deploy_page', 'down')
        request = test_request(accounts.LoginView.as_view(), just_request=True)
        response = deploy_page(accounts.LoginView.as_view())(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Deploy in progress', response.content.decode('utf-8'))

    def test_deploy_page_on(self):
        """Test Enabled Deploy Page"""
        call_command('deploy_page', 'up')
        request = test_request(accounts.LoginView.as_view(), just_request=True)
        response = deploy_page(accounts.LoginView.as_view())(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Deploy in progress', response.content.decode('utf-8'))

    def test_permanent_message(self):
        """Test Permanent Message Middleware"""
        test_message = 'Test Message'
        Setting.set('banner:enabled', namespace='supervisr.core', value=True)
        Setting.set('banner:message', namespace='supervisr.core', value=test_message)
        Setting.set('banner:level', namespace='supervisr.core', value='info')
        request = test_request(common.IndexView.as_view(),
                               just_request=True,
                               user=self.system_user)
        response = permanent_message(common.IndexView.as_view())(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_message in response.content.decode('utf-8'))
        self.assertEqual(response.content.decode('utf-8').count(test_message), 1)

    def test_permanent_message_dupe(self):
        """Test Permanent Message Middleware (message exists already)"""
        test_message = 'Test Message'
        test_level = 'info'
        Setting.set('banner:enabled', namespace='supervisr.core', value=True)
        Setting.set('banner:message', namespace='supervisr.core', value=test_message)
        Setting.set('banner:level', namespace='supervisr.core', value=test_level)
        request = test_request(common.IndexView.as_view(),
                               just_request=True,
                               user=self.system_user)
        messages.add_message(request, getattr(messages, test_level.upper()), test_message)
        response = permanent_message(common.IndexView.as_view())(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_message in response.content.decode('utf-8'))
        self.assertEqual(response.content.decode('utf-8').count(test_message), 1)

    def test_impersonate(self):
        """Test Impersonate Middleware"""
        other_user = User.objects.create(
            username='test2',
            first_name='test user',
            email='test@test.test'
        )
        # Test Impersonation start
        req_imper = test_request(common.IndexView.as_view(), just_request=True, req_kwargs={
            '__impersonate': other_user.pk
        }, user=self.system_user)
        setattr(req_imper, 'session', {})
        res_imper = impersonate(common.IndexView.as_view())(req_imper)
        self.assertEqual(res_imper.status_code, 200)
        self.assertIn('test user', res_imper.content.decode('utf-8'))
        # Test un-impersonate
        rep_unim = test_request(common.IndexView.as_view(), just_request=True, req_kwargs={
            '__unimpersonate': None
        }, user=self.system_user)
        setattr(rep_unim, 'session', {
            'impersonate_id': other_user.pk
        })
        res_unim = impersonate(common.IndexView.as_view())(rep_unim)
        self.assertEqual(res_unim.status_code, 200)
        self.assertNotIn('test user', res_unim.content.decode('utf-8'))
