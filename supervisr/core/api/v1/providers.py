"""Supervisr Core Provider APIv1"""

from celery.result import GroupResult
from django.http import Http404
from django.shortcuts import get_object_or_404

from supervisr.core.api.models import UserAcquirableModelAPI
from supervisr.core.forms.providers import ProviderForm
from supervisr.core.models import ProviderInstance, ProviderTriggerMixin
from supervisr.core.providers.base import get_providers
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.utils import class_to_path, path_to_class


class ProviderAPI(UserAcquirableModelAPI):
    """Provider API"""
    model = ProviderInstance
    form = ProviderForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ALLOWED_VERBS['GET'].extend(['get_all', 'trigger_update'])

    # pylint: disable=unused-argument
    def get_all(self, request, data):
        """Return list of all possible providers"""
        return get_providers(path=True)

    def trigger_update(self, request, data):
        """Trigger provider update"""
        instance_class = data.get('instance_class')
        instance_pk = data.get('instance_pk')
        action = ProviderAction(data.get('provider_action', 1))
        model = path_to_class(instance_class)
        if not issubclass(model, ProviderTriggerMixin):
            raise Http404
        instance = get_object_or_404(model, pk=instance_pk)
        args = (action, class_to_path(instance.__class__), instance.pk)
        group_result = request.user.task_apply_async(ProviderMultiplexer(), *args)
        group_result.wait()
        result = group_result.children[0]
        if isinstance(result, GroupResult):
            return result.join()
        return result.get()
