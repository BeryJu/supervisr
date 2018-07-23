"""Supervisr Core Account APIv1"""

from supervisr.core.api.models import ModelAPI
from supervisr.core.models import Product, User


class AccountAPI(ModelAPI):
    """Account API"""

    model = User

    editable_fields = []

    ALLOWED_VERBS = {
        'GET': ['me', 'has_product']
    }

    # pylint: disable=invalid-name,unused-argument
    def me(self, request, data):
        """Return ourselves as dict"""
        user_data = {}
        for field in ['pk', 'first_name', 'email', 'username']:
            user_data[field] = getattr(request.user, field)
        user_data['id'] = request.user.pk
        return user_data

    def has_product(self, request, data):
        """Check if we have access to product"""
        product = None
        if 'product_pk' in data:
            product = Product.objects.filter(pk=data.get('product_pk'))
        elif 'product_name' in data:
            product = Product.objects.filter(name=data.get('product_name'))

        if product and product.exists():
            if product.first() in request.user.product_set.all():
                return {'result': True}

        return {'result': False}
