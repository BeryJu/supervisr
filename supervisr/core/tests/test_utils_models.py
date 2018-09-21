"""supervisr core utils.models tests"""

from supervisr.core.models import Product, ProductExtension
from supervisr.core.utils.constants import TEST_DOMAIN
from supervisr.core.utils.models import walk_m2m
from supervisr.core.utils.tests import TestCase


class TestModelsUtils(TestCase):
    """test model utils"""

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name=TEST_DOMAIN)
        self.ext = ProductExtension.objects.create(
            extension_name='test')
        self.ext2 = ProductExtension.objects.create(
            extension_name='test2')
        self.product.extensions.add(self.ext)
        self.product.extensions.add(self.ext2)

    def test_walk_m2m(self):
        """Test walk_m2m"""
        results = walk_m2m(self.product)
        self.assertIn(self.product, results)
        self.assertIn(self.ext, results)

    def test_walk_m2m_exclude(self):
        """Test walk_m2m (exclude_classes)"""
        self.assertNotIn(self.ext, walk_m2m(self.product, exclude_classes=[ProductExtension]))

    def test_walk_m2m_only(self):
        """Test walk_m2m (only_classes)"""
        self.assertIn(self.product, walk_m2m(self.product, only_classes=[Product]))
