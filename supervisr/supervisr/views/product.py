from django.contrib.auth.models import User
from django.shortcuts import render, get_list_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from ..models import *

@login_required
def index(req):
    products = Product.objects.filter(invite_only=False)
    return render(req, 'product/index.html', {
        'products': products
    })

@login_required
def view(req, slug):
    product = get_list_or_404(Product, slug=slug)[0]
    # If the product is not invite_only
    # and the user is not associated with the product
    if product.invite_only == False or \
        UserProductRelationship.objects.filter(user=req.user, product=product).exists():
        return render(req, 'product/view.html', {
            'product': product
        })
    raise Http404

@login_required
def new(rew):
    pass

@login_required
def edit(rew):
    pass
