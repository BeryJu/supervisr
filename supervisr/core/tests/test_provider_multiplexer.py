"""supervisr core multiplexer tests"""
from supervisr.core.models import Domain
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.tests.constants import TEST_DOMAIN
from supervisr.core.tests.utils import TestCase
from supervisr.core.utils import class_to_path


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
        self.assertEqual(multiplexer.run(ProviderAction.SAVE, self.domain_path,
                                         self.domain.pk, invoker=self.system_user.pk), 1)

    def test_get_translator(self):
        """Test `ProviderMultiplexer`.`get_translator`"""
        multiplexer = ProviderMultiplexer()
        self.assertIsNone(
            multiplexer.get_translator(self.domain, self.domain.provider_instance.provider,
                                       iteration=100))
