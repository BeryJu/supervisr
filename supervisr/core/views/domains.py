"""
Supervisr Core Domain Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView


class DomainIndexView(GenericIndexView):
    """Show an overview over all domains"""

    model = Domain
    template = 'domain/index.html'

    def get_instance(self) -> HttpResponse:
        return self.model.objects.filter(users__in=[self.request.user]).order_by('domain_name')

# pylint: disable=too-many-ancestors
class DomainNewView(BaseWizardView):
    """Wizard to create a Domain"""

    title = _("New Domain")
    form_list = [DomainForm]
    registrars = None

    def get_form(self, step=None, data=None, files=None) -> DomainForm:
        form = super(DomainNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            providers = get_providers(filter_sub=['domain_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])
            form.fields['provider_instance'].queryset = provider_instance
            form.request = self.request
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs) -> HttpResponse:
        domain = form_dict['0'].save()
        UserAcquirableRelationship.objects.create(
            model=domain,
            user=self.request.user)
        messages.success(self.request, _('Domain successfully created'))
        return redirect(reverse('domain-index'))

class DomainEditView(GenericUpdateView):
    """Update Domain"""

    model = Domain
    form = DomainForm

    def redirect(self, instance: Domain) -> HttpResponse:
        return redirect(reverse('domain-index'))

    def get_instance(self) -> QuerySet:
        """Get domain from name"""
        return self.model.objects.filter(domain=self.kwargs.get('domain'),
                                         users__in=[self.request.user])

    def update_form(self, form: DomainForm) -> DomainForm:
        """Add providers to domainForm"""
        # Create list of all possible provider instances
        providers = get_providers(filter_sub=['domain_provider'], path=True)
        provider_instance = ProviderInstance.objects.filter(
            provider_path__in=providers,
            useracquirablerelationship__user__in=[self.request.user])
        form.fields['provider'].queryset = provider_instance
        form.request = self.request
        return form

class DomainDeleteView(GenericDeleteView):
    """Delete domain"""

    model = Domain

    def redirect(self, instance: Domain) -> HttpResponse:
        return redirect(reverse('domain-index'))

    def get_instance(self) -> QuerySet:
        """Get domain from name"""
        return self.model.objects.filter(domain=self.kwargs.get('domain'),
                                         users__in=[self.request.user])
