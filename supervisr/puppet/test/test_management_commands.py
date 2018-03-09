"""Supervisr Core ManagementCommands Test"""

from unittest import expectedFailure

from django.contrib.auth.models import Group
from django.test import TestCase

from supervisr.core.models import User, get_system_user
from supervisr.core.test.utils import call_command_ret
from supervisr.puppet.models import PuppetModule


class TestManagementCommands(TestCase):
    """Supervisr Core ManagementCommands Test"""

    def setUp(self):
        ps_group = Group.objects.get_or_create(
            name='Puppet Systemusers')[0]
        system_user = User.objects.get(pk=get_system_user())
        ps_group.user_set.add(system_user)
        PuppetModule.objects.get_or_create(
            name='supervisr_core',
            owner=system_user,
            source_path='supervisr/core/server/config/')

    def test_sv_puppet_debug_build(self):
        """Test puppet module build"""
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

    # pylint: disable=invalid-name
    def test_sv_puppet_debug_build_inv_json(self):
        """Test puppet module build with invalid metadata json"""
        pass

    # def test_sv_puppet_import(self):
    #     """
    #     Test PuppetForge import
    #     """
    #     self.assertEqual(call_command_ret('sv_puppet_import', '--module', 'beryju-windows_oem'),
    #                      'Done!\n')
    #     self.assertEqual(call_command_ret('sv_puppet_import', '--module', 'beryju-windows_oem'),
    #                      'Done!\n')

    @expectedFailure
    # pylint: disable=invalid-name
    def test_sv_puppet_import_invalid_user(self):
        """Test Invalid PuppetForge Import (wrong username)"""
        call_command_ret('sv_puppet_import', '--module', 'wrong_name-wrong_name')

    @expectedFailure
    # pylint: disable=invalid-name
    def test_sv_puppet_import_invalid_mod(self):
        """Test Invalid PuppetForge Import (wrong module)"""
        call_command_ret('sv_puppet_import', '--module', 'puppetlabs-wrong_name')
