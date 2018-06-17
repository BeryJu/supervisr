"""supervisr Static views"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from supervisr.static.models import StaticPage


class PageView(View):
    """Render and show a static page"""

    def get(self, request: HttpRequest, slug: str, lang: str = 'en') -> HttpResponse:
        """Render and show a static page"""
        if request.user.is_superuser:
            query = Q(slug=slug)
        else:
            query = Q(slug=slug) & Q(published=True)
        page = get_object_or_404(StaticPage, query & Q(language=lang))
        page.views += 1
        page.save()
        related_langs = StaticPage.objects \
            .filter(query) \
            .exclude(pk=page.pk) \
            .values_list('language', flat=True)
        return render(request, page.template, {
            'page': page,
            'related_langs': related_langs
        })


class FeedView(View):
    """Show a feed with all pages"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Show a feed with all pages"""
        if request.user.is_superuser:
            query = Q()
        else:
            query = Q(published=True) & Q(listed=True)
        all_pages = StaticPage.objects.filter(query).order_by('-created')
        paginator = Paginator(all_pages, request.user.rows_per_page)

        page = request.GET.get('page')
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            pages = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            pages = paginator.page(paginator.num_pages)

        return render(request, 'static/feed.html', {
            'pages': pages
        })
