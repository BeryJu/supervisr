"""Supervisr Core Product Views Views"""
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from supervisr.core.decorators import ifapp
from supervisr.core.forms.products import ProductForm
from supervisr.core.models import Product, UserAcquirableRelationship
from supervisr.core.views.generic import AdminRequiredView, GenericIndexView
from supervisr.core.views.wizards import BaseWizardView


class ProductIndexView(GenericIndexView):
    """Show an Index of all Products that a user can access"""

    model = Product
    template = 'product/index.html'

    def get_instance(self) -> QuerySet:
        return self.model.filter(invite_only=False)


@login_required
def view(request: HttpRequest, slug: str) -> HttpResponse:
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
        try:
            static = redirect_to_static(request, slug)
            if static:
                return static
            raise Http404
        except Http404:
            return render(request, 'product/view.html', {
                'product': product
            })
    raise Http404


class ProductAdminIndex(GenericIndexView, AdminRequiredView):
    """Show all products for admins"""

    model = Product
    template = 'product/admin_index.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.all()


@method_decorator(permission_required('supervisr_core.core_product_can_create'), name='dispatch')
class ProductNewWizard(BaseWizardView):
    """Wizard to create a Product"""

    title = _("New Product")
    form_list = [ProductForm]

    def finish(self, form_list) -> HttpResponse:
        """stuff"""
        pass
