"""Supervisr Core ManagementCommands Test"""
import os

from django.core.management import call_command

from supervisr.core.middleware.deploy_page_middleware import DEPLOY_PAGE_PATH
from supervisr.core.utils.tests import TestCase, call_command_ret


class TestManagementCommands(TestCase):
    """Supervisr Core ManagementCommands Test"""

    def test_deploy_page_mode(self):
        """Test Deploy Page Mode's add_arguments"""
        call_command('deploy_page', 'up')
        self.assertTrue(os.path.exists(DEPLOY_PAGE_PATH))
        call_command('deploy_page', 'down')
        self.assertFalse(os.path.exists(DEPLOY_PAGE_PATH))

    def test_settings(self):
        """Test Setting command"""
        call_command_ret('setting', 'getall')
        call_command_ret('setting', 'list')
        call_command_ret('setting', 'get', 'supervisr.core/install_id')

    def test_template_syntax(self):
        """Test check_template_syntax command"""
        call_command_ret('check_template_syntax')

    def test_migrate_all(self):
        """Test check_migrate_all command"""
        call_command_ret('migrate_all')

    def tearDown(self):
        """Set page down in cleaup"""
        call_command('deploy_page', 'down')
