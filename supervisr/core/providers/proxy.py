"""supervisr core provider proxy"""
import logging
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
from django.db.models import Model

from supervisr.core.models import ProviderInstance, StagedProviderChange

LOGGER = logging.getLogger(__name__)

class ProviderProxy(object):
    """Proxy changes from individual Models, stage them and notify individual Providers"""

    def _build_model_path(instance: Model) -> str:
        """Get app_label.model_name from from instance"""
        ctype = ContentType.objects.get_for_model(instance)
        return '%s.%s' % (ctype.app_label, ctype.model)

    def on_model_saved(self, instance: Model, providers: List[ProviderInstance], created: bool):
        """create StagedProviderChange from saved model"""
        action = StagedProviderChange.ACTION_UPDATE
        if created:
            action = StagedProviderChange.ACTION_CREATE
        for provider_instance in providers:
            change = StagedProviderChange.objects.create(
                provider_instance=provider_instance,
                action=action,
                model_path=ProviderProxy._build_model_path(instance),
                body=serialize('json', [instance, ])
            )
            LOGGER.debug("Staged change %s", change)

    def on_model_deleted(self, instance: Model, providers: List[ProviderInstance]):
        """create StagedProviderChange from deleted model"""
        for provider_instance in providers:
            change = StagedProviderChange.objects.create(
                provider_instance=provider_instance,
                action=StagedProviderChange.ACTION_DELETE,
                model_path=ProviderProxy._build_model_path(instance),
                body=serialize('json', [instance, ])
            )
            LOGGER.debug("Staged change %s", change)
