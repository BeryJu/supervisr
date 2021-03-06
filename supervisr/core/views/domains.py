"""Supervisr Core Domain Views"""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView,
                                          LoginRequiredMixin)
from supervisr.core.views.wizards import BaseWizardView


class DomainIndexView(GenericIndexView):
    """Show an overview over all domains"""

    model = Domain
    template = 'domain/index.html'

    def get_instance(self) -> HttpResponse:
        return self.model.objects.filter(users__in=[self.request.user]).order_by('domain_name')


# pylint: disable=too-many-ancestors
class DomainNewView(LoginRequiredMixin, BaseWizardView):
    """Wizard to create a Domain"""

    title = _("New Domain")
    form_list = [DomainForm]
    registrars = None

    def get_form(self, step=None, data=None, files=None) -> DomainForm:
        form = super(DomainNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            providers = get_providers(capabilities=['domain'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])
            form.fields['provider_instance'].queryset = provider_instance
            form.request = self.request
        return form

    def finish(self, form) -> HttpResponse:
        domain = form.save()
        UserAcquirableRelationship.objects.create(
            model=domain,
            user=self.request.user)
        messages.success(self.request, _('Domain successfully created'))
        return redirect(reverse('domain-index'))


class DomainEditView(GenericUpdateView):
    """Update Domain"""

    model = Domain
    form = DomainForm
    redirect_view = 'domain-index'

    def get_form(self, *args, instance: Domain, **kwargs) -> DomainForm:
        """Add providers to domainForm"""
        form = super().get_form(*args, instance=instance, **kwargs)
        # Create list of all possible provider instances
        providers = get_providers(capabilities=['domain'], path=True)
        provider_instance = ProviderInstance.objects.filter(
            provider_path__in=providers,
            useracquirablerelationship__user__in=[self.request.user])
        form.fields['provider_instance'].queryset = provider_instance
        form.request = self.request
        return form


class DomainDeleteView(GenericDeleteView):
    """Delete domain"""

    model = Domain
    redirect_view = 'domain-index'
