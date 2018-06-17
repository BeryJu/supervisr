"""Supervisr Core ProductView Test"""

from supervisr.core.models import Product
from supervisr.core.test.utils import TestCase, test_request
from supervisr.core.views import products


class TestProductViews(TestCase):
    """Supervisr Core ProductView Test"""

    def test_index_view(self):
        """Test Product Index"""
        self.assertEqual(test_request(products.ProductIndexView.as_view(),
                                      user=self.system_user).status_code, 200)

    def test_product_view(self):
        """Test Product view"""
        test_product = Product.objects.create(
            name="test product",
            slug="test-product",
            description="test product",
            invite_only=False)
        self.assertEqual(test_request(products.view,
                                      user=self.system_user,
                                      url_kwargs={
                                          'slug': test_product.slug
                                      }).status_code, 200)
