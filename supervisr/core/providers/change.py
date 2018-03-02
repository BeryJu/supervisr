"""supervisr core provider proxy"""
import json
import logging
from typing import List

from deepdiff import DeepDiff
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
from django.db.models import Model

from supervisr.core.models import ProviderInstance, StagedProviderChange

LOGGER = logging.getLogger(__name__)

class ChangeBuilder(object):
    """Build changes from individual Models, stage them and notify individual Providers"""

    def build_diff(self, provider_instance: ProviderInstance, model_path: str = None) -> list:
        """Build a dict of all changes for model_path."""
        diffs = []
        changes = StagedProviderChange.objects.filter(
            provider_instance=provider_instance,
        )
        if model_path:
            changes = changes.filter(model_path=model_path)
        changes = changes.order_by('created')

        # Instance creation hasn't been merged yet, and it should be deleted so just ignore it
        if changes.first().action == StagedProviderChange.ACTION_DELETE and \
            changes.last().action == StagedProviderChange.ACTION_CREATE:
            return []

        base_state = json.loads(changes.last().body)
        for change in changes:
            change_body = json.loads(change.body)
            diff = DeepDiff(base_state, change_body)
            if diff != {}:
                diffs.append({
                    'created': change.created,
                    'changes': diff,
                    'model_path': change.model_path
                })
        return diffs

    def build_state(self, provider_instance: ProviderInstance,
                    model_path: str = None) -> StagedProviderChange:
        """Build current state for model_path based on provider_instance"""
        # merged_changes is used to carry all changes. it is never written to the database
        merged_change = StagedProviderChange(
            provider_instance=provider_instance,
            model_path=model_path
        )

        changes = StagedProviderChange.objects.filter(
            provider_instance=provider_instance,
        )
        if model_path:
            changes = changes.filter(model_path=model_path)
        changes = changes.order_by('created')

        # when the last event is delete, we just return now
        if changes.last().action == StagedProviderChange.ACTION_DELETE:
            return merged_change

        data_dict = json.loads(changes.first().body)
        for change in changes:
            change_dict = json.loads(change.body)
            data_dict.update(change_dict)

        LOGGER.debug("Fast forwarded %d changes", len(changes))
        return merged_change

    @staticmethod
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
                model_path=ChangeBuilder._build_model_path(instance),
                body=serialize('json', [instance, ])
            )
            LOGGER.debug("Staged change %s", change)

    def on_model_deleted(self, instance: Model, providers: List[ProviderInstance]):
        """create StagedProviderChange from deleted model"""
        for provider_instance in providers:
            change = StagedProviderChange.objects.create(
                provider_instance=provider_instance,
                action=StagedProviderChange.ACTION_DELETE,
                model_path=ChangeBuilder._build_model_path(instance),
                body=serialize('json', [instance, ])
            )
            LOGGER.debug("Staged change %s", change)
