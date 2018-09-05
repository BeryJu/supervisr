"""supervisr core provider tasks"""
from logging import getLogger
from typing import Iterable

from celery import states
from celery.exceptions import Ignore
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Model

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import ProviderInstance, get_system_user
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
    return []  # This should never be reached, since either we return early or raise


@CELERY_APP.task(bind=True, max_retries=10, base=SupervisrTask)
def provider_signal_handler(self, action: ProviderAction, model: str, model_pk, **kwargs):
    """Forward signal to ProviderMultiplexer"""
    self.prepare(**kwargs)
    model_class = path_to_class(model)
    instance = get_instance(model_class, model_pk)
    system_user = get_system_user()
    multiplexer = ProviderMultiplexer()
    del kwargs['invoker']

    if action == ProviderAction.SAVE:
        LOGGER.debug("provider_signal_handler post_save")
        multiplexer.on_model_saved(system_user, instance, instance.provider_instances, **kwargs)
    elif action == ProviderAction.DELETE:
        LOGGER.debug("provider_signal_handler pre_delete")
        multiplexer.on_model_deleted(system_user, instance, instance.provider_instances)


@CELERY_APP.task(bind=True, max_retries=10, base=SupervisrTask)
def provider_do_save(self, provider_pk: int, model: str, model_pk, created: bool, **kwargs):
    """Run the actual saving procedure and keep trying on failure"""
    self.prepare(**kwargs)
    LOGGER.debug("Starting provider_do_save")
    try:
        self.progress.set(1)
        count = 0
        result = 0
        provider_object_generator = provider_resolve_helper(provider_pk, model, model_pk)
        for provider_object in provider_object_generator:
            result |= provider_object.save(created)
            count += 1
            self.progress.set(count)
        self.progress.set(100)
        LOGGER.debug("Saved instance.")
        return result
    except ProviderRetryException as exc:
        LOGGER.warning(exc)
        self.retry(args=[provider_pk, model, model_pk], countdown=2 ** self.request.retries)
    except SupervisrProviderException as exc:
        self.update_state(
            state=states.FAILURE,
            meta=str(exc)
        )
        # ignore the task so no other state is recorded
        raise Ignore()


@CELERY_APP.task(bind=True, max_retries=10, base=SupervisrTask)
def provider_do_delete(self, provider_pk: int, model: str, model_pk, **kwargs):
    """Run the actual deletion procedure and keep trying on failure"""
    self.prepare(**kwargs)
    try:
        self.progress.set(1)
        count = 0
        result = 0
        provider_object_generator = provider_resolve_helper(provider_pk, model, model_pk)
        for provider_object in provider_object_generator:
            result |= provider_object.delete()
            count += 1
            self.progress.set(count)
        self.progress.set(100)
        LOGGER.debug("Deleted instance.")
        return result
    except ProviderRetryException as exc:
        LOGGER.warning(exc)
        self.retry(args=[provider_pk, model, model_pk], countdown=2 ** self.request.retries)
    except SupervisrProviderException as exc:
        self.update_state(
            state=states.FAILURE,
            meta=str(exc)
        )
        # ignore the task so no other state is recorded
        raise Ignore()
