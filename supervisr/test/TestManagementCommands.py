"""
Supervisr Core ManagementCommands Test
"""

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from ..models import Setting, UserProfile, get_system_user


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

    def test_cleanup(self):
        """
        Test Cleanup
        """
        sys_user = User.objects.get(pk=get_system_user())
        user_prof = UserProfile.objects.create(user=sys_user)
        user_prof.delete() # Set's this to be purged
        call_command('sv_cleanup')
        self.assertEqual(len(UserProfile.objects.all()), 0)
