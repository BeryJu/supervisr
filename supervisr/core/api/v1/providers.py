"""Supervisr Core Provider APIv1"""
from celery.result import GroupResult
from django.shortcuts import get_object_or_404

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.providers import ProviderForm
from supervisr.core.models import ProviderInstance, ProviderTriggerMixin
from supervisr.core.providers.base import get_providers
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.utils import class_to_path
from supervisr.core.utils.models import walk_m2m


class ProviderAPI(UserAcquirableModelAPI):
    """Provider API"""
    model = ProviderInstance
    form = ProviderForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ALLOWED_VERBS['GET'].extend(['get_all', 'trigger_update'])

    def get_all(self, request, data):
        """Return list of all possible providers"""
        return get_providers(path=True)

    def trigger_update(self, request, data):
        """Trigger update for ProviderInstance's children"""
        action = ProviderAction(int(data.get('action', 1)))
        provider_instance = get_object_or_404(ProviderInstance, uuid=data.get('uuid'))
        # Get all affected models we need to trigger
        classes = walk_m2m(provider_instance, only_classes=[ProviderTriggerMixin])
        results = {}
        for instance in classes:
            args = (action, class_to_path(instance.__class__), instance.pk)
            group_result = request.user.task_apply_async(ProviderMultiplexer(), *args)
            group_result.wait()
            result = group_result.children[0]
            if isinstance(result, GroupResult):
                results[str(instance)] = result.join()
            results[str(instance)] = result.get()
        return results
