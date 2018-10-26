"""Supervisr Core Settings Form test"""

from supervisr.core.forms.settings import SettingsForm
from supervisr.core.models import Setting
from supervisr.core.utils.tests import TestCase


class TestSettingsForm(TestCase):
    """Supervisr Core Settings Form test"""

    class TestForm(SettingsForm):
        """Test form"""
        namespace = 'supervisr.core'
        settings = ['test']

        attrs_map = {
            'test': {'placeholder': 'test placeholder'},
        }

    def setUp(self):
        Setting.set('test', 'test')
        super().setUp()

    def test_settings_form_empty(self):
        """Test settings form"""
        form = TestSettingsForm.TestForm()
        form.is_valid()

    def test_settings_form_data(self):
        """Test settings form"""
        form = TestSettingsForm.TestForm(data={'test': 'other value'})
        form.is_valid()
        form.save()
        # self.assertEqual(Setting.get('test'), 'other value')
