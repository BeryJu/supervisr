"""Supervisr DNS Views"""
from django.contrib import messages
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.graph import GraphView
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.reverse_zones import ReverseZoneForm
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import (BaseRecord, DataRecord, ReverseZone,
                                  SetRecord, Zone)


class RecordIndexView(GenericIndexView):
    """Show a list of all records for zone"""

    model = BaseRecord
    template = 'dns/zones/record_index.html'
    zone = None

    def get_instance(self) -> QuerySet:
        self.zone = get_object_or_404(Zone,
                                      uuid=self.kwargs.get('uuid'),
                                      users__in=[self.request.user])
        # TODO: Check this zone=self.zone for validity
        return self.model.objects.filter(zone=self.zone,
                                         users__in=[self.request.user]).order_by('name')

    def update_kwargs(self, kwargs: dict) -> dict:
        kwargs['zone'] = self.zone
        kwargs['is_reverse'] = isinstance(self.zone.cast(), ReverseZone)
        return kwargs


class ZoneGraphView(GraphView):
    """Show a graph of Zone-Record relationships"""

    model = Zone

    def get_label(self, model: Model) -> str:
        if isinstance(model, Zone):
            return 'Zone | %s' % str(model)
        if isinstance(model, SetRecord):
            return 'Set | Name "%s"' % model.name
        elif isinstance(model, DataRecord):
            return 'Data | Name "%s" | Type "%s" | Content "%s"' % \
                    (model.name, model.type, model.content)
        return super().get_label(model)


class ZoneIndexView(GenericIndexView):
    """Show list of user's zones"""

    model = Zone
    template = 'dns/zones/index.html'

    def get_instance(self):
        return super().get_instance().order_by('domain__domain_name')


class ReverseZoneIndexView(GenericIndexView):
    """Show list of user's ReverseZone's"""

    model = ReverseZone
    template = 'dns/zones_reverse/index.html'

    def get_instance(self):
        return super().get_instance().order_by('zone_ip')


# pylint: disable=too-many-ancestors
class ReverseZoneNewView(BaseWizardView):
    """Wizard to create a blank Zone"""

    title = _('New Zone')
    form_list = [ReverseZoneForm]

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            providers = get_providers(capabilities=['dns'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])

            form.fields['providers'].queryset = provider_instance
        return form

    def finish(self, form):
        zone = form.save(commit=False)
        zone.save()
        zone.update_provider_m2m(form.cleaned_data.get('providers'))
        zone.save(force_update=True)
        UserAcquirableRelationship.objects.create(
            model=zone,
            user=self.request.user)
        messages.success(self.request, _('Reverse DNS Zone successfully created'))
        return redirect(reverse('supervisr_dns:index'))


# pylint: disable=too-many-ancestors
class ZoneNewView(BaseWizardView):
    """Wizard to create a blank Zone"""

    title = _('New Zone')
    form_list = [ZoneForm]

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
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

    def finish(self, form):
        zone = form.save(commit=False)
        zone.save()
        zone.update_provider_m2m(form[0].cleaned_data.get('providers'))
        zone.save(force_update=True)
        UserAcquirableRelationship.objects.create(
            model=zone,
            user=self.request.user)
        messages.success(self.request, _('DNS Zone successfully created'))
        return redirect(reverse('supervisr_dns:index'))


class ZoneUpdateView(GenericUpdateView):
    """Update a Zone"""

    model = Zone
    form = ZoneForm
    redirect_view = 'supervisr_dns:index'

    def get_form(self, *args, instance, **kwargs) -> ZoneForm:
        form = super().get_form(*args, instance=instance, **kwargs)
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


class ZoneDeleteView(GenericDeleteView):
    """Delete a Zone"""

    model = Zone
    redirect_view = 'supervisr_dns:index'
