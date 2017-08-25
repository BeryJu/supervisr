"""
Supervisr Static Model Test
"""

import os
import time

from django.contrib.auth.models import User
from django.test import TestCase

from supervisr.core.models import get_system_user
from supervisr.static.models import FilePage


class TestModels(TestCase):
    """
    Supervisr Static Model Test
    """

    def setUp(self):
        # Create temporary file to create page from
        self.content = 'testtestpeoqir901324jioeaer'
        self.filename = 'test-%s.txt' % time.time()
        with open(self.filename, 'w') as file:
            file.write(self.content)

    def tearDown(self):
        # Delete temporary file again
        os.remove(self.filename)

    def test_file_page_update(self):
        """
        Make file page to read from test file
        """
        fpage = FilePage.objects.create(
            path=self.filename,
            author=User.objects.get(pk=get_system_user()))
        fpage.update_from_file()
        self.assertEqual(fpage.content, self.content)
