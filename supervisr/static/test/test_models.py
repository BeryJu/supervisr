"""Supervisr Static Model Test"""

import os
import time

from supervisr.core.test.utils import TestCase
from supervisr.static.models import FilePage


class TestModels(TestCase):
    """Supervisr Static Model Test"""

    def setUp(self):
        super(TestModels, self).setUp()
        # Create temporary file to create page from
        self.content = 'testtestpeoqir901324jioeaer'
        self.filename = 'test-%s.txt' % time.time()
        with open(self.filename, 'w') as file:
            file.write(self.content)

    def tearDown(self):
        # Delete temporary file again
        os.remove(self.filename)

    def test_file_page_update(self):
        """Make file page to read from test file"""
        file_page = FilePage.objects.create(
            path=self.filename,
            author=self.system_user)
        file_page.update_from_file()
        self.assertEqual(file_page.content, self.content)

    def test_file_page_update_dupe(self):
        """Update file page twice"""
        file_page = FilePage.objects.create(
            path=self.filename,
            author=self.system_user)
        file_page.update_from_file()
        file_page.update_from_file()
        self.assertEqual(file_page.content, self.content)
