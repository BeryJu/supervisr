"""
Supervisr OAuth2 Views
"""

import logging

from django.http import Http404
from oauth2_provider.views.base import AuthorizationView

from supervisr.core.models import UserProductRelationship

LOGGER = logging.getLogger(__name__)

class SupervisrAuthorizationView(AuthorizationView):
    """
    Custom OAuth2 Authorization View which checks for invite_only products
    """

    def get(self, request, *args, **kwargs):
        """
        Check if request.user has a relationship with product
        """
        full_res = super(SupervisrAuthorizationView, self).get(request, *args, **kwargs)
        # now self.oauth2_data['application'] is set
        app = self.oauth2_data['application']
        if app.productextensionoauth2_set.exists() and \
            app.productextensionoauth2_set.first().product_set.exists():
            # Only check if there is a connection from OAuth2 Application to product
            product = app.productextensionoauth2_set.first().product_set.first()
            upr = UserProductRelationship.objects.filter(user=request.user, product=product)
            # Product is invite_only = True and no relation with user exists
            if product.invite_only and not upr.exists():
                LOGGER.error("User '%s' has no invitation to '%s'", request.user, product)
                raise Http404
        return full_res
