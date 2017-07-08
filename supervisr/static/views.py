"""
Supervisr Static views
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from supervisr.static.models import StaticPage


def view(req, slug):
    """
    Render and show static page
    """
    if req.user.is_authenticated():
        query = Q(slug=slug)
    else:
        query = Q(slug=slug) & Q(published=True)
    page = StaticPage.objects.filter(query)
    if not page.exists():
        raise Http404
    r_page = page.first()

    return render(req, r_page.template, {
        'page': r_page,
        })

def feed(req):
    """
    Show a feed with all pages
    """
    if req.user.is_authenticated():
        all_pages = StaticPage.objects.all()
    else:
        all_pages = StaticPage.objects.filter(published=True)
    all_pages = all_pages.order_by('-created')
    paginator = Paginator(all_pages, 25) # Show 25 entries per page

    page = req.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pages = paginator.page(paginator.num_pages)

    return render(req, 'static/feed.html', {
        'pages': pages
        })
