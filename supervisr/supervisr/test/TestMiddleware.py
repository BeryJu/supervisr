"""
Supervisr Core Middleware Test
"""

import os

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..middleware.MaintenanceMode import maintenance_mode
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
        Setting.set('supervisr:maintenancemode', True)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(account.login)(req)
        self.assertEqual(res.status_code, 200)

    def test_maintenance_mode_on(self):
        """
        Test Disabled Maintenance Mode
        """
        Setting.set('supervisr:maintenancemode', False)
        req = self.factory.get(reverse('account-login'))
        req.user = AnonymousUser()
        res = maintenance_mode(account.login)(req)
        self.assertEqual(res.status_code, 200)
