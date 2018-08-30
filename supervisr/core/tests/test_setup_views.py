"""supervisr core setup tests"""

from supervisr.core.models import Setting
from supervisr.core.tests.utils import TestCase, test_request
from supervisr.core.views.setup import SetupWizard


class TestSetupViews(TestCase):
    """Test setup wizard"""

    def test_setup_welcome(self):
        """Test welcome page"""
        Setting.set('setup:is_fresh_install', True)
        resp = test_request(SetupWizard.as_view(url_name='setup'), url_kwargs={'step': 'welcome'})
        self.assertEqual(resp.status_code, 200)

    def test_migrate(self):
        """Test migration runner"""
        wizard = SetupWizard()
        for _migration, result in wizard.run_migrate().items():
            self.assertEqual(result, 'success')