"""
Supervisr Puppet View Test
"""

from django.test import TestCase

from supervisr.core.test.utils import test_request
from supervisr.puppet import views
from supervisr.puppet.utils import ForgeImporter


# pylint: disable=duplicate-code
class TestPuppetViews(TestCase):
    """
    Supervisr Puppet View Test
    """

    def test_module_list(self):
        """
        Test module_list view
        """
        self.assertEqual(test_request(views.module_list).status_code, 501)

    def test_module(self):
        """
        Test module view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule'}
        self.assertEqual(test_request(views.module, url_kwargs=kwargs).status_code, 501)

    def test_user_list(self):
        """
        Test user_list view
        """
        self.assertEqual(test_request(views.user_list).status_code, 501)

    def test_user(self):
        """
        Test user view
        """
        kwargs = {'user': 'testuser'}
        self.assertEqual(test_request(views.user, url_kwargs=kwargs).status_code, 501)

    def test_release(self):
        """
        Test release view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule', 'version': '0.1.1'}
        self.assertEqual(test_request(views.release, url_kwargs=kwargs).status_code, 501)

    def test_release_list(self):
        """
        Test release_list view
        """
        # Import a module so the template is not empty
        importer = ForgeImporter()
        importer.import_module('puppetlabs-ntp')
        self.assertEqual(test_request(views.release_list).status_code, 200)
