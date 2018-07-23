"""Supervisr Puppet View Test"""

import json
from shutil import rmtree

from django.contrib.auth.models import Group

from supervisr.core.models import Setting
from supervisr.core.tests.utils import TestCase, test_request
from supervisr.puppet.api.v1 import forge_api
from supervisr.puppet.builder import ReleaseBuilder
from supervisr.puppet.models import PuppetModule


class TestPuppetForgeAPI(TestCase):
    """Supervisr Puppet View Test"""

    key = ''

    @staticmethod
    def is_json(data):
        """Test if data is valid json."""
        try:
            json.loads(data.decode('utf-8'))
        except ValueError:
            return False
        return True

    def setUp(self):
        """Build supervisr-supervisr_core module once"""
        super(TestPuppetForgeAPI, self).setUp()
        ps_group, _group_created = Group.objects.get_or_create(
            name='Puppet Systemusers')
        ps_group.user_set.add(self.system_user)
        PuppetModule.objects.get_or_create(
            name='supervisr_core',
            owner=self.system_user,
            source_path='supervisr/core/server/config/')
        _builder = ReleaseBuilder()
        _builder.set_module(PuppetModule.objects.filter(name='supervisr_core').first())
        _builder.run()
        TestPuppetForgeAPI.is_json(b'{')
        self.key = Setting.get('url_key', namespace='supervisr.puppet')

    def tearDown(self):
        """Cleanup"""
        _builder = ReleaseBuilder()
        _builder.set_module(PuppetModule.objects.filter(name='supervisr_core').first())
        rmtree(_builder.output_base)

    def test_module_list(self):
        """Test module_list view"""
        self.assertEqual(test_request(forge_api.module_list).status_code, 501)

    def test_module(self):
        """Test module view"""
        # test invalid user
        self.assertEqual(test_request(forge_api.module,
                                      url_kwargs={
                                          'user': 'invalid_user',
                                          'module': 'supervisr_core',
                                      }).status_code, 404)
        # test invalid module
        self.assertEqual(test_request(forge_api.module,
                                      url_kwargs={
                                          'user': 'supervisr',
                                          'module': 'invalid_module',
                                      }).status_code, 404)
        # Test correct data
        resp = test_request(forge_api.module,
                            url_kwargs={
                                'user': 'supervisr',
                                'module': 'supervisr_core',
                            })
        self.assertEqual(TestPuppetForgeAPI.is_json(resp.content), True)
        self.assertEqual(resp.status_code, 200)

    def test_user_list(self):
        """Test user_list view"""
        self.assertEqual(test_request(forge_api.user_list).status_code, 501)

    def test_user(self):
        """Test user view"""
        kwargs = {'user': 'testuser'}
        self.assertEqual(test_request(forge_api.user, url_kwargs=kwargs).status_code, 501)

    def test_release(self):
        """Test release view"""
        # test invalid user
        self.assertEqual(test_request(forge_api.release,
                                      url_kwargs={
                                          'user': 'invalid_user',
                                          'module': 'supervisr_core',
                                          'version': '1.0.0',
                                      }).status_code, 404)
        # test invalid module
        self.assertEqual(test_request(forge_api.release,
                                      url_kwargs={
                                          'user': 'supervisr',
                                          'module': 'invalid_module',
                                          'version': '1.0.0',
                                      }).status_code, 404)
        # test invalid version
        # test invalid module
        self.assertEqual(test_request(forge_api.release,
                                      url_kwargs={
                                          'user': 'supervisr',
                                          'module': 'supervisr_core',
                                          'version': '0.0.0',
                                      }).status_code, 404)
        # test correct data
        resp = test_request(forge_api.release,
                            url_kwargs={
                                'user': 'supervisr',
                                'module': 'supervisr_core',
                                'version': '1.0.0',
                            })
        self.assertEqual(TestPuppetForgeAPI.is_json(resp.content), True)
        self.assertEqual(resp.status_code, 200)

    def test_release_list(self):
        """Test release_list view"""
        # Import a module so the template is not empty
        self.assertEqual(test_request(forge_api.release_list).status_code, 200)
        self.assertEqual(test_request(
            forge_api.release_list,
            req_kwargs={'module': 'supervisr_core'}).status_code, 200)
        self.assertEqual(test_request(
            forge_api.release_list,
            req_kwargs={'module': 'supervisr-supervisr_core'}).status_code, 200)

    def test_file(self):
        """Test File download"""
        self.assertEqual(test_request(
            forge_api.file,
            url_kwargs={
                'user': 'supervisr',
                'version': '1.0.0',
                'module': 'supervisr_core',
                'key': 'wrong_key',
            }).status_code, 404)
        self.assertEqual(test_request(
            forge_api.file,
            url_kwargs={
                'user': 'supervisr',
                'version': '1.0.0',
                'module': 'supervisr_core',
                'key': self.key
            }).status_code, 200)
