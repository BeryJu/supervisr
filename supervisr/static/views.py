"""
Supervisr Static views
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from supervisr.static.models import StaticPage


def view(req, slug, lang='en'):
    """
    Render and show static page
    """
    if req.user.is_superuser:
        query = Q(slug=slug)
    else:
        query = Q(slug=slug) & Q(published=True)
    page = StaticPage.objects.filter(query & Q(language=lang))
    if not page.exists():
        raise Http404
    r_page = page.first()
    r_page.views += 1
    r_page.save()
    related_langs = StaticPage.objects \
        .filter(query) \
        .exclude(pk=r_page.pk) \
        .values_list('language', flat=True)
    return render(req, r_page.template, {
        'page': r_page,
        'related_langs': related_langs
        })

def feed(req):
    """
    Show a feed with all pages
    """
    if req.user.is_superuser:
        query = Q()
    else:
        query = Q(published=True) & Q(listed=True)
    all_pages = StaticPage.objects.filter(query)
    all_pages = all_pages.order_by('-created')
    paginator = Paginator(all_pages, req.user.rows_per_page)

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
