"""
Supervisr Core ManagementCommands Test
"""

from django.core.management import call_command
from django.test import TestCase

from ..models import Setting


# pylint: disable=duplicate-code
class TestManagementCommandss(TestCase):
    """
    Supervisr Core ManagementCommands Test
    """

    def test_maintenance_mode(self):
        """
        Test Maintenance Mode's add_arguments
        """
        call_command('sv_maintenance', 'on')
        self.assertTrue(Setting.get('supervisr:maintenancemode'), True)
        call_command('sv_maintenance', 'off')
        self.assertTrue(Setting.get('supervisr:maintenancemode'), False)
