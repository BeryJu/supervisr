"""supervisr mod stats influx view tests"""

from supervisr.core.tests.utils import TestCase, test_request
from supervisr.mod.stats.influx.views import SettingsView


class TestViews(TestCase):
    """Test Views"""

    def test_form_test_send(self):
        """Test 'test' button"""
        test_request(SettingsView.as_view(), method='POST', req_kwargs={'test': ''})
