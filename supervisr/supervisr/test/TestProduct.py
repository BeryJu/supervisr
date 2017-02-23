"""
Supervisr Core Product Test
"""

import os

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Product, UserProductRelationship


# pylint: disable=duplicate-code
class TestProduct(TestCase):
    """
    Supervisr Core Product Test
    """

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.product_a = Product.objects.create(
            name="Test Product A",
            slug="test-product-a",
            description="Test Product A with auto_add=True",
            price=0.000,
            auto_add=True)
        self.assertEqual(self.product_a.pk, 1)
        self.user = User.objects.create(
            username="Test User a",
            email="testa@test.test")
        self.assertNotEqual(self.user.pk, None)

    def test_auto_add(self):
        """
        Test Product's auto_add
        """
        Product.do_auto_add(self.user)
        rel = UserProductRelationship.objects.filter(
            product=self.product_a,
            user=self.user)
        self.assertTrue(rel.exists())

    def test_auto_add_all(self):
        """
        Test Product's auto_all_add
        """
        product_b = Product.objects.create(
            name="Test Product B",
            slug="test-product-b",
            description="Test Product B with auto_all_add=True",
            price=0.000,
            auto_all_add=True)
        self.assertEqual(product_b.pk, 2)
        rel = UserProductRelationship.objects.filter(
            product=product_b,
            user=self.user)
        self.assertTrue(rel.exists())