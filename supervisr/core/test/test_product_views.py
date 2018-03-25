"""
Supervisr Core ProductView Test
"""
import os

from django.test import RequestFactory, TestCase
from django.urls import reverse

from supervisr.core.models import Product, User, get_system_user
from supervisr.core.views import products


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
        request = self.factory.get(reverse('product-index'))
        request.user = User.objects.get(pk=get_system_user())
        response = products.index(request)
        self.assertEqual(response.status_code, 200)

    def test_product_view(self):
        """
        Test Product view
        """
        test_product = Product.objects.create(
            name="test product",
            slug="test-product",
            description="test product",
            invite_only=False)
        request = self.factory.get(reverse('product-view', kwargs={
            'slug': test_product.slug
        }))
        request.user = User.objects.get(pk=get_system_user())
        response = products.index(request)
        self.assertEqual(response.status_code, 200)
