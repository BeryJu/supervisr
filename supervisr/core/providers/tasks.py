"""supervisr core provider tasks"""
from logging import getLogger
from typing import Iterable

from celery.exceptions import Ignore
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Model

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import ProviderInstance
from supervisr.core.providers.exceptions import (ProviderRetryException,
                                                 SupervisrProviderException)
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.tasks import SupervisrTask
from supervisr.core.utils import path_to_class

LOGGER = getLogger(__name__)


def get_instance(model: Model, model_pk) -> Model:
    """Get Model instance from DB"""
    try:
        return model.objects.get(pk=model_pk)
    except (MultipleObjectsReturned, model.DoesNotExist) as exc:
        raise SupervisrProviderException from exc


def provider_resolve_helper(provider_pk: int, model_path: str, model_pk) -> Iterable:
    """Helper function to do all the actual work in tasks, except for error handling"""
    # multiplexer is used to get responsible translator
    multiplexer = ProviderMultiplexer()
    # Convert to actual python class since we only pass the path
    # so we don't have to use pickle serialization
    model_class = path_to_class(model_path)
    # Get root provider to get translator from
    root_provider = get_instance(ProviderInstance, provider_pk).provider
    # Lookup model instance from DB
    model_instance = get_instance(model_class, model_pk)
    # Do the actual translator lookup
    translator = multiplexer.get_translator(model_instance, root_provider)
    if not translator:
        return []
    # Convert to provider_object, this fuction wraps the errors
    # and converts them to SupervisrProviderException
    try:
        return translator.to_external(model_instance)
    except Exception as exc:  # noqa
        raise SupervisrProviderException from exc


@CELERY_APP.task(bind=True, max_retries=10, base=SupervisrTask)
def provider_do_work(self, action: ProviderAction, provider_pk: int,
                     model: str, model_pk, **kwargs):
    """Run the actual saving procedure of a single provider and keep trying on failure"""
    self.prepare(**kwargs)
    LOGGER.debug("Starting provider_do_work %r", action)
    try:
        self.progress.set(1)
        count = 0
        results = []
        provider_object_generator = provider_resolve_helper(provider_pk, model, model_pk)
        for provider_object in provider_object_generator:
            result = None
            if action == ProviderAction.SAVE:
                result = provider_object.save(**kwargs)
            elif action == ProviderAction.DELETE:
                result = provider_object.delete(**kwargs)
            count += 1
            results.append((provider_object.__class__.__name__, result))
            self.progress.set(count)
            LOGGER.debug("\tUpdated instance %r", provider_object)
        self.progress.set(100)
        return {provider_pk: results}
    except ProviderRetryException as exc:
        LOGGER.warning(exc)
        raise self.retry(args=[action, provider_pk, model, model_pk], kwargs=kwargs,
                         countdown=2 ** self.request.retries)
    except SupervisrProviderException as exc:
        # self.update_state(
        #     state=states.FAILURE,
        #     meta={'error': str(exc)})
        # ignore the task so no other state is recorded
        raise Ignore()
