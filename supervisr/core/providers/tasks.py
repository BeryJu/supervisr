"""supervisr core provider tasks"""
from logging import getLogger

from django.db.models import Model

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import ProviderInstance
from supervisr.core.providers.exceptions import SupervisrProviderException
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.utils import path_to_class

LOGGER = getLogger(__name__)


def get_instance(model: Model, model_pk: int) -> Model:
    """Get Model instance from DB"""
    try:
        return model.objects.get(model_pk)
    except (Model.MultipleObjectsReturned, Model.DoesNotExist) as exc:
        raise SupervisrProviderException from exc


def provider_resolve_helper(provider_pk: int, model_path: str, model_pk: int):
    """Helper function to do all the actual work in tasks, except for error handling"""
    # multiplexer is used to get responsible translator
    multiplexer = ProviderMultiplexer()
    # Convert to actual python class since we only pass the path
    # so we don't have to use pickle serialization
    model_class = path_to_class(model_path)
    # Get root provider to get translator from
    root_provider = get_instance(ProviderInstance, provider_pk)
    # Lookup model instance from DB
    model_instance = get_instance(model_class, model_pk)
    # Do the actual translator lookup
    translator = multiplexer.get_translator(model_instance, root_provider)
    # Convert to provider_object, this fuction wraps the errors
    # and converts them to SupervisrProviderException
    try:
        return translator.to_external(model_instance)
    except Exception as exc:  # noqa
        raise SupervisrProviderException from exc
    return None  # This should never be reached, since either we return early or raise


@CELERY_APP.task(bind=True, max_retries=10)
def provider_do_save(self, provider_pk: int, model: str, model_pk: int):
    """Run the actual saving procedure and keep trying on failure"""
    try:
        provider_object = provider_resolve_helper(provider_pk, model, model_pk)
        provider_object.save()
        LOGGER.debug("Saved instance.")
    except SupervisrProviderException:
        self.retry(args=[provider_object], countdown=2 ** self.request.retries)


@CELERY_APP.task(bind=True, max_retries=10)
def provider_do_delete(self, provider_pk: int, model: str, model_pk: int):
    """Run the actual deletion procedure and keep trying on failure"""
    try:
        provider_object = provider_resolve_helper(provider_pk, model, model_pk)
        provider_object.delete()
        LOGGER.debug("Deleted instance.")
    except SupervisrProviderException:
        self.retry(args=[provider_object], countdown=2 ** self.request.retries)
