"""
Supervisr Core Middleware Test
"""

import os

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..middleware.MaintenanceMode import maintenance_mode
from ..middleware.PermanentMessage import permanent_message
from ..models import Setting
from ..views import account


# pylint: disable=duplicate-code
class TestMiddleware(TestCase):
    """
    Supervisr Core Middleware Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_maintenance_mode_off(self):
        """
        Test Enabled Maintenance Mode
        """
        Setting.set('core:maintenancemode', True)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(account.login)(req)
        self.assertEqual(res.status_code, 200)

    def test_maintenance_mode_on(self):
        """
        Test Disabled Maintenance Mode
        """
        Setting.set('core:maintenancemode', False)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(account.login)(req)
        self.assertEqual(res.status_code, 200)

    def test_permanent_message(self):
        """
        Test Permanent Message Middleware
        """
        test_message = 'Test Message'
        Setting.set('core:banner:enabled', True)
        Setting.set('core:banner:message', test_message)
        Setting.set('core:banner:level', 'info')
        req = self.factory.get(reverse('account-login'))
        # Fix django.contrib.messages.api.MessageFailure
        # because this request doesn't have a session or anything
        setattr(req, 'session', 'session')
        setattr(req, '_messages', FallbackStorage(req))
        req.user = AnonymousUser()
        res = permanent_message(account.login)(req)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(test_message in res.content.decode('utf-8'))
        self.assertEqual(res.content.decode('utf-8').count(test_message), 1)

    def test_permanent_message_dupe(self):
        """
        Test Permanent Message Middleware (message exists already)
        """
        test_message = 'Test Message'
        test_level = 'info'
        Setting.set('core:banner:enabled', True)
        Setting.set('core:banner:message', test_message)
        Setting.set('core:banner:level', test_level)
        req = self.factory.get(reverse('account-login'))
        # Fix django.contrib.messages.api.MessageFailure
        # because this request doesn't have a session or anything
        setattr(req, 'session', 'session')
        setattr(req, '_messages', FallbackStorage(req))
        messages.add_message(req, getattr(messages, test_level.upper()), test_message)
        req.user = AnonymousUser()
        res = permanent_message(account.login)(req)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(test_message in res.content.decode('utf-8'))
        self.assertEqual(res.content.decode('utf-8').count(test_message), 1)
