"""
Supervisr Core Product Views Views
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from supervisr.core.decorators import ifapp
from supervisr.core.forms.product import ProductForm
from supervisr.core.models import Product, UserAcquirableRelationship
from supervisr.core.views.wizards import BaseWizardView


@login_required
def index(request):
    """Show an Index of all Products that a user can access"""
    products = Product.objects.filter(invite_only=False)
    return render(request, 'product/index.html', {
        'products': products
    })

@login_required
def view(request, slug):
    """Show more specific Information about a product"""
    @ifapp('supervisr_static')
    def redirect_to_static(request, slug):
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
def admin_index(request):
    """Show product overview for admins"""
    products = Product.objects.all()
    return render(request, 'product/admin_index.html', {
        'products': products
        })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
# pylint: disable=too-many-ancestors
class ProductNewWizard(BaseWizardView):
    """Wizard to create a Product"""

    title = _("New Product")
    form_list = [ProductForm]
    registrars = None

    # def get_form(self, step=None, data=None, files=None):
    #     form = super(ProductNewWizard, self).get_form(step, data, files)
    #     if step is None:
    #         step = self.steps.current
    #     if step == '0':
    #         providers = get_providers(filter_sub=['domain_provider'], path=True)
    #         provider_instance = ProviderInstance.objects.filter(
    #             provider_path__in=providers,
    #             useracquirablerelationship__user__in=[self.request.user])
    #         form.fields['provider'].queryset = provider_instance
    #         form.request = self.request
    #     return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        domain = form_dict['0'].save(commit=False)
        domain.name = domain.domain
        domain.save()
        UserAcquirableRelationship.objects.create(
            model=domain,
            user=self.request.user)
        messages.success(self.request, _('Product successfully created'))
        return redirect(reverse('domain-index'))
