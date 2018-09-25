"""supervisr core provider action views"""
from logging import getLogger
from typing import Union

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from supervisr.core.models import CastableModel, Domain, ProviderTriggerMixin
from supervisr.core.providers.multiplexer import ProviderMultiplexer
from supervisr.core.providers.objects import ProviderAction
from supervisr.core.utils import class_to_path
from supervisr.core.views.generic import GenericModelView

LOGGER = getLogger(__name__)

class ProviderUpdateView(GenericModelView):
    """View to trigger provider update and show results"""

    template_name = 'provider/actions-update.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        """Show status"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        return render(request, self.template_name, {'instance': instance})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Start task and redirect to ourselves with task_id"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        if not isinstance(instance, ProviderTriggerMixin):
            raise ValueError('Model instance must inherit `ProviderTriggerMixin`')
        action = ProviderAction(int(request.POST.get('action')))
        # Start multiplexer
        LOGGER.debug("ProviderTriggerMixin post_save")
        args = (action, class_to_path(instance.__class__), instance.pk)
        kwargs = {'created': False, 'user_triggered': True}
        # User permissions are not checked here since they are checked in
        # GenericModelView.get_instance
        request.user.task_apply_async(ProviderMultiplexer(), *args, **kwargs)
        return self.redirect(instance)

    def redirect(self, instance) -> Union[HttpResponse, str]:
        return HttpResponseRedirect('')


class ProviderUpdateViewTest(ProviderUpdateView):
    """Test class"""

    model = Domain
