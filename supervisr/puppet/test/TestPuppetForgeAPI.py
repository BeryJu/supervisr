"""
Supervisr Puppet View Test
"""

import shutil

from django.test import TestCase

from supervisr.core.models import Setting
from supervisr.core.test.utils import test_request
from supervisr.puppet.utils import ForgeImporter
from supervisr.puppet.views import forge_api


class TestPuppetForgeAPI(TestCase):
    """
    Supervisr Puppet View Test
    """

    importer = None

    def test_module_list(self):
        """
        Test module_list view
        """
        self.assertEqual(test_request(forge_api.module_list).status_code, 501)

    def test_module(self):
        """
        Test module view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule'}
        self.assertEqual(test_request(forge_api.module, url_kwargs=kwargs).status_code, 501)

    def test_user_list(self):
        """
        Test user_list view
        """
        self.assertEqual(test_request(forge_api.user_list).status_code, 501)

    def test_user(self):
        """
        Test user view
        """
        kwargs = {'user': 'testuser'}
        self.assertEqual(test_request(forge_api.user, url_kwargs=kwargs).status_code, 501)

    def test_release(self):
        """
        Test release view
        """
        kwargs = {'user': 'testuser', 'module': 'testmodule', 'version': '0.1.1'}
        self.assertEqual(test_request(forge_api.release, url_kwargs=kwargs).status_code, 501)

    def test_release_list(self):
        """
        Test release_list view
        """
        # Import a module so the template is not empty
        self.importer = ForgeImporter()
        self.importer.import_module('beryju-windows_oem')
        self.assertEqual(test_request(forge_api.release_list).status_code, 200)
        self.assertEqual(test_request(
            forge_api.release_list,
            req_kwargs={'module': 'windows_oem'}).status_code, 200)
        self.assertEqual(test_request(
            forge_api.release_list,
            req_kwargs={'module': 'beryju-windows_oem'}).status_code, 200)

    def test_file(self):
        """
        Test File download
        """
        self.importer = ForgeImporter()
        self.importer.import_module('beryju-windows_oem')
        user_agent = Setting.get('allowed_user_agent', namespace='supervisr.puppet')
        self.assertEqual(test_request(
            forge_api.file,
            url_kwargs={
                'user': 'beryju',
                'version': '1.0.0',
                'module': 'windows_oem'},
            headers={
                'HTTP_USER_AGENT': 'invalid_user_agent'
            }).status_code, 404)
        self.assertEqual(test_request(
            forge_api.file,
            url_kwargs={
                'user': 'beryju',
                'version': '1.0.0',
                'module': 'windows_oem'},
            headers={
                'HTTP_USER_AGENT': user_agent
            }).status_code, 200)

    def tearDown(self):
        """
        Clean up after importer
        """
        if self.importer:
            shutil.rmtree(self.importer.output_base+"/*", ignore_errors=True)
