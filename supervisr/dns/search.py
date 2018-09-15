"""supervisr dns search handlers"""
from django.dispatch import receiver
from django.http import HttpRequest
from django.shortcuts import reverse

from supervisr.core.signals import on_search
from supervisr.core.views.search import DefaultSearchHandler
from supervisr.dns.models import DataRecord, SetRecord, Zone


class ZoneSearchHandler(DefaultSearchHandler):
    """Search Handler for Zone"""

    model = Zone
    fields = ['domain__domain_name']
    icon = 'router'
    view_name = 'supervisr_dns:index'

    def get_label(self, instance, request: HttpRequest) -> str:
        """Return label for SearchResult."""
        return instance.domain.domain_name


class DataRecordSearchHandler(DefaultSearchHandler):
    """Search Handler for DataRecord"""

    model = DataRecord
    fields = ['name']
    icon = 'view-list'

    def get_url(self, instance, request: HttpRequest) -> str:
        """Return full URL for SearchResult."""
        return reverse('supervisr_dns:index')


class SetRecordSearchHandler(DefaultSearchHandler):
    """Search Handler for SetRecord"""

    model = SetRecord
    fields = ['name']
    icon = 'view-list'

    def get_url(self, instance, request: HttpRequest) -> str:
        """Return full URL for SearchResult."""
        return reverse('supervisr_dns:index')


@receiver(on_search)
# pylint: disable=unused-argument
def search_handler(sender, query, request, *args, **kwargs):
    """Inbuilt search handler for DNS models"""
    return DefaultSearchHandler.combine(handlers=[ZoneSearchHandler,
                                                  DataRecordSearchHandler,
                                                  SetRecordSearchHandler],
                                        query=query, request=request)
