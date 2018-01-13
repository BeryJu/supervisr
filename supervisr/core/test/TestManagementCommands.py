"""Supervisr Core ManagementCommands Test"""
import os

from django.core.management import call_command
from django.test import TestCase

from supervisr.core.middleware.DeployPageMiddleware import DEPLOY_PAGE_PATH


class TestManagementCommands(TestCase):
    """Supervisr Core ManagementCommands Test"""

    def test_deploy_page_mode(self):
        """Test Deploy Page Mode's add_arguments"""
        call_command('deploy_page', 'up')
        self.assertTrue(os.path.exists(DEPLOY_PAGE_PATH))
        call_command('deploy_page', 'down')
        self.assertFalse(os.path.exists(DEPLOY_PAGE_PATH))
