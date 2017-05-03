"""
Supervisr Core ManagementCommands Test
"""

from unittest import expectedFailure

from django.test import TestCase

from supervisr.core.test.utils import call_command_ret


# pylint: disable=duplicate-code
class TestManagementCommandss(TestCase):
    """
    Supervisr Core ManagementCommands Test
    """

    def test_sv_puppet_debug_build(self):
        """
        Test puppet module build
        """
        self.assertEqual(call_command_ret('sv_puppet_debug_build',
                                          '--module', 'supervisr-supervisr_core'),
                         'Built Module supervisr_core!\n')
        self.assertEqual(call_command_ret('sv_puppet_debug_build',
                                          '--module', 'supervisr_core'),
                         'Built Module supervisr_core!\n')
        self.assertEqual(call_command_ret('sv_puppet_debug_build',
                                          '--module', 'wrong_name-wrong_name'),
                         'User wrong_name doesn\'t exist!\n')
        self.assertEqual(call_command_ret('sv_puppet_debug_build',
                                          '--module', 'wrong_name'),
                         'Module supervisr-wrong_name doesn\'t exist!\n')

    # pylint: disable=invalid-name, no-self-use
    def test_sv_puppet_debug_build_inv_json(self):
        """
        Test puppet module build with invalid metadata json
        """
        pass

    def test_sv_puppet_import(self):
        """
        Test PuppetForge import
        """
        self.assertEqual(call_command_ret('sv_puppet_import', '--module', 'puppetlabs-ntp'),
                         'Done!\n')
        self.assertEqual(call_command_ret('sv_puppet_import', '--module', 'puppetlabs-ntp'),
                         'Done!\n')

    @expectedFailure
    # pylint: disable=invalid-name, no-self-use
    def test_sv_puppet_import_invalid_user(self):
        """
        Test Invalid PuppetForge Import (wrong username)
        """
        call_command_ret('sv_puppet_import', '--module', 'wrong_name-wrong_name')

    @expectedFailure
    # pylint: disable=invalid-name, no-self-use
    def test_sv_puppet_import_invalid_mod(self):
        """
        Test Invalid PuppetForge Import (wrong module)
        """
        call_command_ret('sv_puppet_import', '--module', 'puppetlabs-wrong_name')
