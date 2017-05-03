"""
Supervisr Core ManagementCommands Test
"""

from django.core.management import call_command
from django.test import TestCase


# pylint: disable=duplicate-code
class TestManagementCommandss(TestCase):
    """
    Supervisr Core ManagementCommands Test
    """

    def test_maintenance_mode(self):
        """
        Test Maintenance Mode's add_arguments
        """
        call_command('sv_puppet_debug_build', '--module', 'supervisr-supervisr_core')
        call_command('sv_puppet_debug_build', '--module', 'supervisr_core')
        call_command('sv_puppet_debug_build', '--module', 'wrong_name-wrong_name')
        call_command('sv_puppet_debug_build', '--module', 'wrong_name')

    def test_sv_puppet_import(self):
        """
        Test PuppetForge import
        """
        # call_command('sv_puppet_import', '--module', 'puppetlabs-ntp')
