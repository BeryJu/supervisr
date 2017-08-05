"""
Supervisr Core Product Views Views
"""

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from supervisr.core.decorators import ifapp
from supervisr.core.models import Product, UserProductRelationship


@login_required
def index(req):
    """
    Show an Index of all Products that a user can access
    """
    products = Product.objects.filter(invite_only=False)
    return render(req, 'product/index.html', {
        'products': products
    })

@login_required
def view(req, slug):
    """
    Show more specific Information about a product
    """
    @ifapp('supervisr/static')
    def redirect_to_static(req, slug):
        """
        if static app is installed, use static's productpage
        """
        from supervisr.static.views import view
        return view(req, slug)
    static = redirect_to_static(req, slug)
    if static:
        return static
    product = get_object_or_404(Product, slug=slug)
    # If the product is not invite_only
    # and the user is not associated with the product
    if product.invite_only is False or \
        UserProductRelationship.objects.filter(user=req.user,
                                               product=product).exists():
        return render(req, 'product/view.html', {
            'product': product
        })
    raise Http404
