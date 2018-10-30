"""Supervisr Core Search Views"""
from collections import OrderedDict
from difflib import SequenceMatcher
from inspect import isclass
from logging import getLogger
from typing import Dict, List

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Q
from django.http import Http404, HttpRequest
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from supervisr.core.models import UserAcquirable
from supervisr.core.signals import on_search
from supervisr.core.utils import get_apps

LOGGER = getLogger(__name__)

class SearchResult:
    """Datastructure for search results"""

    label = ''
    similarity_percent = 0
    """How close the query is to the name of the object, in percent (1-100)"""
    url = ''
    icon = 'unknown-status'
    __type = None


class SearchQuery:
    """Datastructure for search queries"""

    filter_app = None
    filter_model = None
    query = ''


class SearchView(TemplateView, LoginRequiredMixin):
    """Search"""

    template_name = 'search/search.html'

    def remap_results(self, results: Dict[callable, SearchResult]) -> Dict[str, SearchResult]:
        """Convert handler_functions to app_label"""
        re_mapped = {}
        app_labels = [app.label for app in get_apps(exclude=[])]
        for app_handler, app_results in results:
            for app_label in app_labels:
                if app_handler.__module__.replace('.', '_').startswith(app_label):
                    # Get AppConfig so we can get App's `verbose_name`
                    app_config = apps.get_app_config(app_label)
                    label = app_config.verbose_name
                    if app_results:
                        re_mapped[label] = app_results
        return OrderedDict(sorted(re_mapped.items()))

    def search(self, query: SearchQuery) -> Dict[str, SearchResult]:
        """Search logic"""
        results = on_search.send(sender=self, query=query, request=self.request)
        results = self.remap_results(results)
        return results

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        query = SearchQuery()
        query.query = self.request.GET.get('q', None)
        query.filter_app = self.request.GET.get('filter_app', None)
        query.filter_model = self.request.GET.get('filter_model', None)
        if not query.query:
            raise Http404
        context['results'] = self.search(query)
        return context

class DefaultSearchHandler:
    """Implements a default set of searching logic."""

    model = None
    """Which Model should be searched"""

    fields = []
    """Which fields of `self.model` should the query be run against"""

    query_operator = 'contains'
    """Operator to use when looking up Model instances."""

    label_field = 'name'
    """Field which is used to create label for `SearchResult`.
    If custom logic is needed, override `self.get_label`."""

    icon = 'unknown-status'
    """Icon which is used to create `SearchResult`.
    If custom logic is needed, override `self.get_icon`."""

    view_name = None
    """View which is reversed to create URL for `SearchResult`.
    If custom logic is needed, override `self.get_url`."""

    view_kwarg_name = None
    """Argument name used in conjunction with `self.view_name` for URL Creation.
    If custom logic is needed, override `self.get_url`."""

    def __init__(self, **kwargs):
        super().__init__()
        for arg, value in kwargs.items():
            setattr(self, arg, value)

    @staticmethod
    def combine(handlers: List['DefaultSearchHandler'],
                query: SearchQuery, request: HttpRequest) -> Dict[Model, List[SearchResult]]:
        """Combine search results from all handlers"""
        results = {}
        for handler in handlers:
            if isclass(handler):
                handler_instance = handler()
            else:
                handler_instance = handler
            results.update(handler_instance.search(query, request))
        return OrderedDict(sorted(results.items(), key=lambda kv: kv[0].__name__))

    @property
    def model_app(self):
        """Get app that `self.model` belongs to."""
        return ContentType.objects.get_for_model(self.model).app_label

    def check_filters(self, query: SearchQuery) -> bool:
        """Check if filters forbid `self.model` or the app that `self.model` belongs to should
        be ignored"""
        if query.filter_app:
            if query.filter_app != self.model_app:
                return False
        if query.filter_model:
            if query.filter_model != self.model.__name__:
                return False
        return True

    def search(self, query: SearchQuery, request: HttpRequest) -> Dict[Model, List[SearchResult]]:
        """filter through `model`, looking at `fields`"""
        # Check filters early
        if not self.check_filters(query):
            return {}
        model_query = Q()
        for field in self.fields:
            model_query = model_query | Q(**{
                '%s__%s' % (field, self.query_operator): query.query
            })
        # Special case for UserAcquirable
        if issubclass(self.model, UserAcquirable):
            model_query = model_query & Q(users__in=[request.user])
        # Get matching objects and create SearchResult objects
        matching = self.model.objects.filter(model_query)
        if not matching.exists():
            return {}
        results = []
        for match in matching:
            result_object = SearchResult()
            result_object.label = self.get_label(match, request)
            result_object.icon = self.get_icon(match, request)
            result_object.url = self.get_url(match, request)
            result_object.similarity_percent = self.get_similarity(match, query, request)
            setattr(result_object, '__type', self.model)
            results.append(result_object)
            LOGGER.debug('Found %s with similarity %d', result_object.label,
                         result_object.similarity_percent)
        # Add special `search only for these kind of object link`
        results.append(self.get_filtered_link(request, query))
        # sort by similarity
        sorted_results = sorted(results, key=lambda item: item.similarity_percent, reverse=True)
        # Return as dict
        return {self.model: sorted_results}

    def get_filtered_link(self, request: HttpRequest, query: SearchQuery) -> SearchResult:
        """Add special `search only for these kind of object link`"""
        special = SearchResult()
        request_get = request.GET.copy()
        # Add a `search only for these objects` if no filter is set,
        # otherwise add link to remove filter
        if query.filter_app and query.filter_model:
            special.label = _('Search everything...')
            del request_get['filter_app']
            del request_get['filter_model']
        else:
            special.label = _('Only search for objects like these...')
            # Add filter attributes to GET
            request_get['filter_app'] = self.model_app
            request_get['filter_model'] = self.model.__name__
        special.url = request.path + '?' + request_get.urlencode()
        special.icon = 'pop-out'
        # Set similarity to 0 so this gets shown last
        special.similarity_percent = 0
        setattr(special, '__special', True)
        return special

    def get_label(self, instance, request: HttpRequest) -> str:
        """Return label for SearchResult."""
        return getattr(instance, self.label_field, 'N/A')

    def get_icon(self, instance, request: HttpRequest) -> str:
        """Return icon name for SearchResult.
        Reference: https://vmware.github.io/clarity/icons/icon-sets"""
        return self.icon

    def get_url(self, instance, request: HttpRequest) -> str:
        """Return full URL for SearchResult."""
        if self.view_kwarg_name:
            return reverse(self.view_name, kwargs={self.view_kwarg_name: instance.pk})
        return reverse(self.view_name)

    def get_similarity(self, instance, query: SearchQuery, request: HttpRequest) -> int:
        """Get similarity (1-100)"""
        return SequenceMatcher(None, query.query, self.get_label(instance, request)).ratio() * 100
