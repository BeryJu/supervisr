"""Supervisr Mail AddressView Test"""

from django.test import TestCase

from supervisr.core.models import get_system_user, UserAcquirableRelationship, User
from supervisr.mail.views import addresses
from supervisr.core.test.utils import test_request
from supervisr.mail.models import Address

class TestAddressViews(TestCase):
    """Supervisr Mail AddressView Test"""

    def test_index_view(self):
        """test index view (anonymous)"""
        self.assertEqual(test_request(addresses.AddressIndexView.as_view()).status_code, 302)

    def test_index_view_auth(self):
        """test index view (authenticated)"""
        self.assertEqual(test_request(addresses.AddressIndexView.as_view(),
                                      user=get_system_user()).status_code, 200)

    def test_new_view_auth(self):
        """test new view (authenticated)"""
        self.assertEqual(test_request(addresses.AddressNewWizard.as_view(),
                                      user=get_system_user()).status_code, 200)

    def test_update_view_auth(self):
        """test update view (authenticated)"""
        address = Address.objects.create(mail_address='test')
        UserAcquirableRelationship.objects.create(
            user=User.objects.get(get_system_user()),
            model=address
            )
        self.assertEqual(test_request(addresses.AddressUpdateView.as_view(),
                                      req_kwargs={
                                          'address': address.mail_address,
                                          'pk': address.pk
                                      },
                                      user=get_system_user()).status_code, 200)

    def test_delete_view_auth(self):
        """test delete view (authenticated)"""
        address = Address.objects.create(mail_address='test')
        UserAcquirableRelationship.objects.create(
            user=User.objects.get(get_system_user()),
            model=address
        )
        self.assertEqual(test_request(addresses.AddressDeleteView.as_view(),
                                      req_kwargs={
                                          'address': address.mail_address,
                                          'pk': address.pk
                                      },
                                      user=get_system_user()).status_code, 200)
