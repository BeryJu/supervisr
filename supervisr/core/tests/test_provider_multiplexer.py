"""supervisr core multiplexer tests"""
from unittest.mock import patch

from celery.result import GroupResult

from supervisr.core.models import Domain
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.utils import class_to_path
from supervisr.core.utils.constants import TEST_DOMAIN
from supervisr.core.utils.tests import TestCase


class TestProviderMultiplexer(TestCase):
    """Test `ProviderMultiplexer`"""

    def setUp(self):
        super().setUp()
        self.domain_path = class_to_path(Domain)
        self.domain = Domain.objects.create(
            domain_name=TEST_DOMAIN,
            provider_instance=self.provider)

    def test_multiplexer(self):
        """Test ProviderMultiplexer"""
        multiplexer = ProviderMultiplexer()
        self.assertIsInstance(multiplexer.run(ProviderAction.SAVE, self.domain_path,
                                              self.domain.pk, invoker=self.system_user.pk),
                              GroupResult)

    @patch('supervisr.mod.provider.debug.providers.core.DebugTranslator.to_external')
    def test_get_translator(self, to_external):
        """Test `ProviderMultiplexer`.`get_translator`"""
        to_external.return_value = None
        multiplexer = ProviderMultiplexer()
        self.assertIsNone(
            multiplexer.get_translator(self.system_user, self.domain.provider_instance.provider,
                                       iteration=100))
