"""
Supervisr Core ProductView Test
"""
import os

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..models import Product, get_system_user
from ..views import product

# pylint: disable=duplicate-code
class TestProductViews(TestCase):
    """
    Supervisr Core ProductView Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.factory = RequestFactory()

    def test_index_view(self):
        """
        Test Product Index
        """
        req = self.factory.get(reverse('product-index'))
        req.user = User.objects.get(pk=get_system_user())
        res = product.index(req)
        self.assertEqual(res.status_code, 200)

    def test_product_view(self):
        """
        Test Product view
        """
        test_product = Product.objects.create(
            name="test product",
            slug="test-product",
            description="test product",
            price=0.000,
            invite_only=False)
        req = self.factory.get(reverse('product-view', kwargs={
            'slug': test_product.slug
            }))
        req.user = User.objects.get(pk=get_system_user())
        res = product.index(req)
        self.assertEqual(res.status_code, 200)
