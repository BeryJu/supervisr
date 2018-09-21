"""supervisr core provider multiplexer"""
from logging import getLogger
from typing import Union

from celery import group
from django.db.models import Model

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import ProviderTriggerMixin
from supervisr.core.providers.base import BaseProvider
from supervisr.core.providers.objects import (ProviderAction,
                                              ProviderObjectTranslator)
from supervisr.core.tasks import SupervisrTask
from supervisr.core.utils import class_to_path, path_to_class

LOGGER = getLogger(__name__)


class ProviderMultiplexer(SupervisrTask):
    """Multiplex signals to all relevent providers"""

    name = 'supervisr.core.providers.multiplexer.ProviderMultiplexer'

    def run(self, action: ProviderAction, model: str, model_pk, **kwargs):
        """Main Provider handler. This function is called as a task from `post_save`,
        `pre_delete` and `m2m_changed`. Function uses `ProviderMultiplexer`

        Args:
            action (ProviderAction): [description]
            model (str): [description]
            model_pk ([type]): [description]
        """
        from supervisr.core.providers.tasks import get_instance
        self.prepare(**kwargs)
        model_class = path_to_class(model)
        instance = get_instance(model_class, model_pk)

        LOGGER.debug("provider_signal_handler %r", action)
        task_group = group(self.get_model_handlers(action, instance, **kwargs))
        return task_group()

    def get_translator(self, instance: Model, root_provider: BaseProvider,
                       iteration=0) -> Union[ProviderObjectTranslator, None]:
        """Recursively walk through providers.
        Limited to 100 iterations to prevent infinite loops

        Args:
            instance(Model): Model instance for which a translator should be found.
            root_provider(BaseProvider): BaseProvider instance which should be walked.
            iteration(int, optional): Defaults to 0. Iteration count to limit infinite loops.

        Returns:
            Union[ProviderObjectTranslator, None]: Translator instance if available otherwise None.
        """
        sub_provider = root_provider.get_provider(type(instance))
        if sub_provider:
            if iteration >= 100:
                LOGGER.debug("Provider walk canceled, 100 iterations reached")
                return None
            sub_provider_instance = sub_provider(root_provider.credentials)
            LOGGER.debug("Redirected from %r to %r", root_provider, sub_provider_instance)
            return self.get_translator(instance, sub_provider_instance, iteration=iteration + 1)
        translator = root_provider.get_translator(type(instance))
        if translator:
            return translator(provider_instance=root_provider)
        return None

    def get_model_handlers(self, action: ProviderAction,
                           instance: ProviderTriggerMixin, **kwargs) -> int:
        """Notify providers that model was saved/deleted so translation can start

        Args:
            action (ProviderAction): Which action to perform
            invoker (User): User invoking the task
            instance (Model): Model instance which has been saved
        """
        from supervisr.core.providers.tasks import provider_do_work
        LOGGER.debug("instance %r, action %r", instance, action)
        for provider in instance.provider_instances:
            LOGGER.debug("\tprovider_instance %r", provider)
            class_path = class_to_path(instance.__class__)
            args = (action, provider.pk, class_path, instance.pk)
            CELERY_APP.control.add_consumer(class_path)
            LOGGER.debug("\tstarted task provider_do_work")
            yield provider_do_work.signature(args, kwargs).set(queue=class_path)


CELERY_APP.tasks.register(ProviderMultiplexer())
