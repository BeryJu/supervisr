"""
Supervisr Mail Form Test
"""

import os

from django.test import TestCase

from ..forms.mail_account import MailAccountFormCredentials


# pylint: disable=duplicate-code
class TestForms(TestCase):
    """
    Supervisr Mail Form Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'


    def test_maccount_cred(self):
        """
        Test Index View (Anonymous)
        """
        form = MailAccountFormCredentials(data={
            'password': 'b3ryjuorg!',
            'password_rep': 'b3ryjuorg!',
            })
        self.assertTrue(form.is_valid())
