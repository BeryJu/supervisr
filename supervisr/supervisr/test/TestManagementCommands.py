"""
Supervisr Core ManagementCommands Test
"""

import os

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
        call_command('maintenance', 'on')
        call_command('maintenance', 'off')
