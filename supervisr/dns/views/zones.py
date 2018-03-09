"""
Supervisr DNS Views
"""

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import Resource, Zone
from supervisr.dns.utils import date_to_soa


class ZoneIndexView(GenericIndexView):
    """Show list of user's zones"""

    model = Zone
    template = 'dns/zones/index.html'

    def get_instance(self):
        return self.model.objects.filter(users__in=[self.request.user]) \
                                 .order_by('domain__domain_name')

# pylint: disable=too-many-ancestors
class ZoneNewView(BaseWizardView):
    """
    Wizard to create a blank Zone
    """

    title = _('New Zone')
    form_list = [ZoneForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(ZoneNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            domains = Zone.objects.filter(users__in=[self.request.user])

            unused_domains = Domain.objects.filter(users__in=[self.request.user]) \
                .exclude(pk__in=domains.values_list('domain', flat=True))

            providers = get_providers(capabilities=['dns'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['providers'].queryset = provider_instance
        return form

    def finish(self, form_list):
        zone = form_list[0].save(commit=False)
        # Zone requires an SOA record
        soa_record = Resource.objects.create(
            name='@',
            type='SOA',
            content='placeholder %s. %d 1800 180 2419200 86400' % (
                self.request.user.email.replace('@', '.'),
                date_to_soa()
            )
        )
        zone.soa = soa_record
        zone.save()
        zone.update_provider_m2m(form_list[0].cleaned_data.get('providers'))
        zone.save(force_update=True)
        UserAcquirableRelationship.objects.create(
            model=zone,
            user=self.request.user)
        UserAcquirableRelationship.objects.create(
            model=soa_record,
            user=self.request.user)
        messages.success(self.request, _('DNS Zone successfully created'))
        return redirect(reverse('supervisr_dns:index'))

class ZoneUpdateView(GenericUpdateView):
    """Update a Zone"""

    model = Zone
    form = ZoneForm

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(domain__domain_name=self.kwargs.get('zone'),
                                         users__in=[self.request.user])

    def update_form(self, form: ZoneForm) -> ZoneForm:
        # Create list of all possible provider instances
        providers = get_providers(capabilities=['dns'], path=True)
        provider_instance = ProviderInstance.objects.filter(
            provider_path__in=providers,
            useracquirablerelationship__user__in=[self.request.user])
        form.fields['providers'].queryset = provider_instance
        return form

    def save(self, form: ZoneForm) -> Zone:
        zone = form.save(commit=False)
        zone.save()
        zone.update_provider_m2m(form.cleaned_data.get('providers'))
        return zone

    def redirect(self, instance: Zone) -> HttpResponse:
        return redirect(reverse('supervisr_dns:index'))

class ZoneDeleteView(GenericDeleteView):
    """Delete a Zone"""

    model = Zone

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(domain__domain_name=self.kwargs.get('zone'),
                                         users__in=[self.request.user])

    def redirect(self, instance: Zone) -> HttpResponse:
        return redirect(reverse('supervisr_dns:index'))
