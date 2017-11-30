"""
Supervisr Core ManagementCommands Test
"""

from django.core.management import call_command
from django.test import TestCase

from supervisr.core.models import Setting


class TestManagementCommandss(TestCase):
    """
    Supervisr Core ManagementCommands Test
    """

    def test_maintenance_mode(self):
        """
        Test Maintenance Mode's add_arguments
        """
        call_command('maintenance', 'on')
        self.assertTrue(Setting.get('maintenancemode', namespace='supervisr.core'), True)
        call_command('maintenance', 'off')
        self.assertTrue(Setting.get('maintenancemode', namespace='supervisr.core'), False)
