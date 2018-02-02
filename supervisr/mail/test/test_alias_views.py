"""
Supervisr Mail AliasView Test
"""

import os

from django.test import TestCase

from supervisr.core.models import get_system_user
from supervisr.core.test.utils import test_request
from supervisr.mail.views import alias


class TestAliasViews(TestCase):
    """
    Supervisr Mail AliasView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def test_index_view(self):
        """
        Test Index View (Anonymous)
        """
        self.assertEqual(test_request(alias.index).status_code, 302)

    def test_index_view_auth(self):
        """
        Test Index View (Authenticated)
        """
        self.assertEqual(test_request(alias.index,
                                      user=get_system_user()).status_code, 200)

    def test_index_view_page_inv(self):
        """
        Test Index View (invalid page)
        """
        self.assertEqual(test_request(alias.index,
                                      user=get_system_user(),
                                      req_kwargs={'page': 2}).status_code, 200)
