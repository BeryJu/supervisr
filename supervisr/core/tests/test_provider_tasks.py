"""supervisr core provider tasks tests"""
from types import GeneratorType
from unittest.mock import patch

from celery.exceptions import Ignore, Retry

from supervisr.core.models import Domain, User
from supervisr.core.providers.exceptions import (ProviderRetryException,
                                                 SupervisrProviderException)
from supervisr.core.providers.objects import (ProviderAction, ProviderObject,
                                              ProviderResult)
from supervisr.core.providers.tasks import (get_instance, provider_do_work,
                                            provider_resolve_helper)
from supervisr.core.tests.constants import TEST_DOMAIN
from supervisr.core.tests.utils import TestCase
from supervisr.core.utils import class_to_path


class TestProviderTasks(TestCase):
    """supervisr core provider tasks tests"""

    def setUp(self):
        super().setUp()
        self.domain_path = class_to_path(Domain)
        self.domain = Domain.objects.create(
            domain_name=TEST_DOMAIN,
            provider_instance=self.provider)

    def test_get_instance(self):
        """Test get_instance (successful)"""
        self.assertEqual(get_instance(User, self.system_user.pk), self.system_user)

    def test_get_instance_fail(self):
        """Test get_instance (unsuccessful)"""
        with self.assertRaises(SupervisrProviderException):
            get_instance(User, 0)

    def test_resolve_helper(self):
        """Test provider_resolve_helper"""
        result = provider_resolve_helper(self.provider.pk, self.domain_path, self.domain.pk)
        self.assertIsInstance(result, GeneratorType)
        result_list = list(result)
        self.assertEqual(len(result_list), 1)
        self.assertIsInstance(result_list[0], ProviderObject)

    def test_resolve_helper_empty(self):
        """Test provider_resolve_helper (empty)"""
        user_path = class_to_path(User)
        self.assertEqual(provider_resolve_helper(
            self.provider.pk, user_path, self.system_user.pk), [])

    @patch('supervisr.mod.provider.debug.providers.translators.core_domain.'
           'DebugDomainTranslator.to_external')
    def test_resolve_helper_fail(self, to_external):
        """Test provider_resolve_helper (throwing error)"""
        to_external.side_effect = RuntimeError('testing')
        with self.assertRaises(SupervisrProviderException):
            provider_resolve_helper(self.provider.pk, self.domain_path, self.domain.pk)

    @patch('supervisr.core.tasks.ProgressRecorder.set')
    # pylint: disable=unused-argument
    def test_provider_do_work(self, progress_set):
        """Test provider_do_work"""
        # Emulate new model created
        # pylint: disable=no-value-for-parameter
        self.assertEqual(provider_do_work(
            ProviderAction.SAVE, self.provider.pk, self.domain_path, self.domain.pk, created=True),
                         ProviderResult.SUCCESS)
        # Emulate delete
        # pylint: disable=no-value-for-parameter
        self.assertEqual(provider_do_work(
            ProviderAction.DELETE, self.provider.pk, self.domain_path, self.domain.pk),
                         ProviderResult.SUCCESS)

    @patch('supervisr.core.providers.tasks.provider_do_work.retry')
    @patch('supervisr.mod.provider.debug.providers.translators.core_domain.'
           'DebugDomainObject.save')
    @patch('supervisr.core.tasks.ProgressRecorder.set')
    # pylint: disable=unused-argument
    def test_provider_do_work_retry(self, progress_set, save, task_retry):
        """Test provider_do_work"""
        # setup mocks
        task_retry.side_effect = Retry()
        save.side_effect = ProviderRetryException('testing')
        # Emulate new model created
        with self.assertRaises(Retry):
            # pylint: disable=no-value-for-parameter
            provider_do_work(ProviderAction.SAVE, self.provider.pk,
                             self.domain_path, self.domain.pk, created=True)

    @patch('supervisr.mod.provider.debug.providers.translators.core_domain.'
           'DebugDomainObject.save')
    @patch('supervisr.core.tasks.ProgressRecorder.set')
    # pylint: disable=unused-argument
    def test_provider_do_work_ignore(self, progress_set, save):
        """Test provider_do_work"""
        # setup mocks
        save.side_effect = SupervisrProviderException('testing')
        # Emulate new model created
        with self.assertRaises(Ignore):
            # pylint: disable=no-value-for-parameter
            provider_do_work(ProviderAction.SAVE, self.provider.pk,
                             self.domain_path, self.domain.pk, created=True)
