"""supervisr core search handlers"""

from django.dispatch import receiver

from supervisr.core.models import Domain, ProviderInstance
from supervisr.core.signals import on_search
from supervisr.core.views.search import DefaultSearchHandler


@receiver(on_search)
# pylint: disable=unused-argument
def search_handler(sender, query, request, *args, **kwargs):
    """Inbuilt search handler for core models"""

    domain_search_handler = DefaultSearchHandler(model=Domain,
                                                 fields=['domain_name', 'description'],
                                                 label_field='domain_name', icon='world',
                                                 view_name='domain-index')

    provider_search_handler = DefaultSearchHandler(model=ProviderInstance,
                                                   fields=['name', 'provider_path'],
                                                   icon='vmw-app',
                                                   view_name='instance-index')

    return DefaultSearchHandler.combine(handlers=[
        domain_search_handler, provider_search_handler], query=query, request=request)
