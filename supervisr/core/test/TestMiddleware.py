"""
Supervisr Core Middleware Test
"""

import os

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.middleware.ImpersonateMiddleware import impersonate
from supervisr.core.middleware.MaintenanceMode import maintenance_mode
from supervisr.core.middleware.PermanentMessage import permanent_message
from supervisr.core.models import Setting, User, get_system_user
from supervisr.core.views import accounts, common


class TestMiddleware(TestCase):
    """
    Supervisr Core Middleware Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()
        self.sys_user = User.objects.get(pk=get_system_user())

    def test_maintenance_mode_off(self):
        """
        Test Enabled Maintenance Mode
        """
        Setting.set('maintenancemode', True)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(accounts.LoginView.as_view())(req)
        self.assertEqual(res.status_code, 200)

    def test_maintenance_mode_on(self):
        """
        Test Disabled Maintenance Mode
        """
        Setting.set('maintenancemode', False)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(accounts.LoginView.as_view())(req)
        self.assertEqual(res.status_code, 200)

    def test_permanent_message(self):
        """
        Test Permanent Message Middleware
        """
        test_message = 'Test Message'
        Setting.set('banner:enabled', namespace='supervisr.core', value=True)
        Setting.set('banner:message', namespace='supervisr.core', value=test_message)
        Setting.set('banner:level', namespace='supervisr.core', value='info')
        request = self.factory.get(reverse('common-index'))
        # Fix django.contrib.messages.api.MessageFailure
        # because this request doesn't have a session or anything
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        request.user = self.sys_user
        res = permanent_message(common.index)(request)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(test_message in res.content.decode('utf-8'))
        self.assertEqual(res.content.decode('utf-8').count(test_message), 1)

    def test_permanent_message_dupe(self):
        """Test Permanent Message Middleware (message exists already)"""
        test_message = 'Test Message'
        test_level = 'info'
        Setting.set('banner:enabled', namespace='supervisr.core', value=True)
        Setting.set('banner:message', namespace='supervisr.core', value=test_message)
        Setting.set('banner:level', namespace='supervisr.core', value=test_level)
        request = self.factory.get(reverse('common-index'))
        # Fix django.contrib.messages.api.MessageFailure
        # because this request doesn't have a session or anything
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        messages.add_message(request, getattr(messages, test_level.upper()), test_message)
        request.user = self.sys_user
        res = permanent_message(common.index)(request)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(test_message in res.content.decode('utf-8'))
        self.assertEqual(res.content.decode('utf-8').count(test_message), 1)

    def test_impersonate(self):
        """Test Impersonate Middleware"""
        other_user = User.objects.create(
            username='test2',
            first_name='test user',
            email='test@test.test'
        )
        # Test Impersonation start
        req_imper = self.factory.get(reverse('common-index'), data={
            '__impersonate': other_user.pk
        })
        setattr(req_imper, 'user', User.objects.get(pk=get_system_user()))
        setattr(req_imper, 'session', {})
        res_imper = impersonate(common.index)(req_imper)
        self.assertEqual(res_imper.status_code, 200)
        self.assertIn('test user', res_imper.content.decode('utf-8'))
        # Test un-impersonate
        rep_unim = self.factory.get(reverse('common-index'), data={
            '__unimpersonate': None
        })
        setattr(rep_unim, 'user', User.objects.get(pk=get_system_user()))
        setattr(rep_unim, 'session', {
            'impersonate_id': other_user.pk
        })
        res_unim = impersonate(common.index)(rep_unim)
        self.assertEqual(res_unim.status_code, 200)
        self.assertNotIn('test user', res_unim.content.decode('utf-8'))
