"""Supervisr DNS Reverse Zone Views"""

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import ProviderInstance, UserAcquirableRelationship
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.reverse_zones import ReverseZoneForm
from supervisr.dns.models import ReverseZone


class ReverseZoneIndexView(GenericIndexView):
    """Show list of user's zones"""

    model = ReverseZone
    template = 'dns/zones_reverse/index.html'

    def get_instance(self):
        return self.model.objects.filter(users__in=[self.request.user]) \
                                 .order_by('zone_ip')


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

    def finish(self, form_list):
        zone = form_list[0].save(commit=False)
        zone.save()
        zone.update_provider_m2m(form_list[0].cleaned_data.get('providers'))
        zone.save(force_update=True)
        UserAcquirableRelationship.objects.create(
            model=zone,
            user=self.request.user)
        messages.success(self.request, _('Reverse DNS Zone successfully created'))
        return redirect(reverse('supervisr_dns:index'))


class ZoneUpdateView(GenericUpdateView):
    """Update a Zone"""

    model = ReverseZone
    form = ReverseZoneForm

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(zone_ip=self.kwargs.get('zone'),
                                         users__in=[self.request.user])

    def get_form(self, *args, instance, **kwargs) -> ReverseZoneForm:
        form = super().get_form(*args, instance=instance, **kwargs)
        # Create list of all possible provider instances
        providers = get_providers(capabilities=['dns'], path=True)
        provider_instance = ProviderInstance.objects.filter(
            provider_path__in=providers,
            useracquirablerelationship__user__in=[self.request.user])
        form.fields['providers'].queryset = provider_instance
        return form

    def save(self, form: ReverseZoneForm) -> ReverseZone:
        zone = form.save(commit=False)
        zone.save()
        zone.update_provider_m2m(form.cleaned_data.get('providers'))
        return zone

    def redirect(self, instance: ReverseZone) -> HttpResponse:
        return redirect(reverse('supervisr_dns:index'))


class ZoneDeleteView(GenericDeleteView):
    """Delete a Zone"""

    model = ReverseZone

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(zone_ip=self.kwargs.get('zone'),
                                         users__in=[self.request.user])

    def redirect(self, instance: ReverseZone) -> HttpResponse:
        return redirect(reverse('supervisr_dns:index'))
