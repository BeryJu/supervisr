"""Supervisr Core ManagementCommands Test"""

from shutil import rmtree

from django.contrib.auth.models import Group

from supervisr.core.utils.tests import TestCase, call_command_ret
from supervisr.puppet.builder import ReleaseBuilder
from supervisr.puppet.models import PuppetModule
from supervisr.puppet.utils import ForgeNotFound


class TestManagementCommands(TestCase):
    """Supervisr Core ManagementCommands Test"""

    def setUp(self):
        super(TestManagementCommands, self).setUp()
        ps_group, _group_created = Group.objects.get_or_create(
            name='Puppet Systemusers')
        ps_group.user_set.add(self.system_user)
        PuppetModule.objects.get_or_create(
            name='supervisr_core',
            owner=self.system_user,
            source_path='supervisr/core/server/config/')

    def tearDown(self):
        _builder = ReleaseBuilder()
        _builder.set_module(PuppetModule.objects.filter(name='supervisr_core').first())
        rmtree(_builder.output_base)

    def test_puppet_debug_build(self):
        """Test puppet module build"""
        self.assertEqual(call_command_ret('puppet_debug_build',
                                          '--module', 'supervisr-supervisr_core'),
                         'Built Module supervisr_core!\n')
        self.assertEqual(call_command_ret('puppet_debug_build',
                                          '--module', 'supervisr_core'),
                         'Built Module supervisr_core!\n')
        self.assertEqual(call_command_ret('puppet_debug_build',
                                          '--module', 'wrong_name-wrong_name'),
                         'User wrong_name doesn\'t exist!\n')
        self.assertEqual(call_command_ret('puppet_debug_build',
                                          '--module', 'wrong_name'),
                         'Module supervisr-wrong_name doesn\'t exist!\n')

    def test_puppet_debug_build_inv_json(self):
        """Test puppet module build with invalid metadata json"""
        pass

    # def test_puppet_import(self):
    #     """
    #     Test PuppetForge import
    #     """
    #     self.assertEqual(call_command_ret('puppet_import', '--module', 'beryju-windows_oem'),
    #                      'Done!\n')
    #     self.assertEqual(call_command_ret('puppet_import', '--module', 'beryju-windows_oem'),
    #                      'Done!\n')

    def test_puppet_import_invalid_user(self):
        """Test Invalid PuppetForge Import (wrong username)"""
        with self.assertRaises(ForgeNotFound):
            call_command_ret('puppet_import', '--module', 'wrong_name-wrong_name')

    def test_puppet_import_invalid_mod(self):
        """Test Invalid PuppetForge Import (wrong module)"""
        with self.assertRaises(ForgeNotFound):
            call_command_ret('puppet_import', '--module', 'puppetlabs-wrong_name')
