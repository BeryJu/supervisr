"""Supervisr Core Product Views Views"""
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from supervisr.core.decorators import ifapp
from supervisr.core.forms.product import ProductForm
from supervisr.core.models import Product, UserAcquirableRelationship
from supervisr.core.views.wizards import BaseWizardView


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Show an Index of all Products that a user can access"""
    products = Product.objects.filter(invite_only=False)
    return render(request, 'product/index.html', {
        'products': products
    })


@login_required
def view(request: HttpRequest, slug) -> HttpResponse:
    """Show more specific Information about a product"""
    @ifapp('supervisr_static')
    def redirect_to_static(request: HttpRequest, slug) -> HttpResponse:
        """if static app is installed, use static's productpage"""
        from supervisr.static.views import PageView
        return PageView.as_view()(request, slug)
    product = get_object_or_404(Product, slug=slug)
    # If the product is not invite_only
    # and the user is not associated with the product
    if product.invite_only is False or \
        UserAcquirableRelationship.objects.filter(user=request.user,
                                                  model=product).exists():
        static = redirect_to_static(request, slug)
        if static:
            return static
        return render(request, 'product/view.html', {
            'product': product
        })
    raise Http404


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_index(request: HttpRequest) -> HttpResponse:
    """Show product overview for admins"""
    products = Product.objects.all()
    return render(request, 'product/admin_index.html', {
        'products': products
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('supervisr_core.core_product_can_create'), name='dispatch')
# pylint: disable=too-many-ancestors
class ProductNewWizard(BaseWizardView):
    """Wizard to create a Product"""

    title = _("New Product")
    form_list = [ProductForm]

    def finish(self, form_list) -> HttpResponse:
        """stuff"""
        pass
