"""supervisr core graph views"""

from unittest.mock import PropertyMock, patch
from defusedxml import ElementTree

from supervisr.core.models import (Product, ProductExtension, User,
                                   UserAcquirableRelationship)
from supervisr.core.utils.constants import TEST_DOMAIN
from supervisr.core.utils.tests import TestCase, test_request
from supervisr.core.views.graph import GraphView


class TestGraphViews(TestCase):
    """Test GraphView"""

    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
            name=TEST_DOMAIN)
        ext = ProductExtension.objects.create(
            extension_name='test')
        self.product.extensions.add(ext)

    @patch.object(GraphView, 'exclude_models', new_callable=PropertyMock)
    @patch.object(GraphView, 'model', new_callable=PropertyMock)
    def test_graph_render_404(self, graphview_model, graphview_exclude):
        """Test GraphView render"""
        graphview_model.return_value = Product
        graphview_exclude.return_value = [User]
        response = test_request(GraphView.as_view(), user=self.system_user, url_kwargs={
            'pk': self.product.pk
        })
        self.assertEqual(response.status_code, 404)

    @patch.object(GraphView, 'exclude_models', new_callable=PropertyMock)
    @patch.object(GraphView, 'model', new_callable=PropertyMock)
    def test_graph_render(self, graphview_model, graphview_exclude):
        """Test GraphView render"""
        graphview_model.return_value = Product
        graphview_exclude.return_value = [User]
        UserAcquirableRelationship.objects.create(
            model=self.product,
            user=self.system_user)
        response = test_request(GraphView.as_view(), user=self.system_user, url_kwargs={
            'uuid': self.product.uuid
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8').count('title'), 8)
        ElementTree.fromstring(response.content.decode('utf-8'))
