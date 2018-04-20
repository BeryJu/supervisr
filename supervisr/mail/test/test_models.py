"""Supervisr Mail Test"""

from django.test import TestCase

from supervisr.core.models import (BaseCredential, ProviderInstance, User,
                                   get_system_user)
from supervisr.mail.models import Account


class TestModels(TestCase):
    """Supervisr Mail Test"""

    def setUp(self):
        self.user = User.objects.get(pk=get_system_user())
        self.provider_credentials = BaseCredential.objects.create(
            owner=self.user, name='test-creds')
        self.provider = ProviderInstance.objects.create(
            provider_path='supervisr.core.providers.base.BaseProvider',
            credentials=self.provider_credentials)

    def test_mailaccount_password(self):
        """
        Test MailAccount's set_password
        """
        mx_account = Account.objects.by(self.user).create(name='unittest-test')
        user = User.objects.get(pk=get_system_user())
        mx_account.set_password(user, 'test', salt='testtest')
        self.assertEqual(mx_account.password, ('$6$rounds=656000$testtest$CaN82QPQ6BrS4VJ7R8Nuxoow'
                                               'ctnCSXRhXnFE4je8MGWN7bIvPsU0yVZgG0ZrPAw44DzIi/NhDng'
                                               'vVkJ7w6B3M0'))
