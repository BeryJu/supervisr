"""
Supervisr DNS record views
"""

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import UserAcquirableRelationship
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.records import RecordForm
from supervisr.dns.models import Record, Zone


class RecordIndexView(GenericIndexView):
    """Show a list of all records for zone"""

    model = Record
    template = 'dns/records/index.html'
    zone = None

    def get_instance(self) -> QuerySet:
        self.zone = get_object_or_404(Zone, domain__domain_name=self.kwargs.get('zone'),
                                      users__in=[self.request.user])
        return self.model.objects.filter(record_zone=self.zone,
                                         users__in=[self.request.user]).order_by('name')

    def update_kwargs(self, kwargs: dict) -> dict:
        kwargs['zone'] = self.zone
        return kwargs


# pylint: disable=too-many-ancestors
class RecordNewView(BaseWizardView):
    """
    Wizard to create a blank Record
    """

    title = _('New Record')
    form_list = [RecordForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(RecordNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            user_zones = Zone.objects.filter(users__in=[self.request.user])
            zone_pk = user_zones.filter(
                domain__domain_name=self.kwargs.get('zone')).first().pk
            form.fields['record_zone'].queryset = user_zones
            form.fields['record_zone'].initial = zone_pk
        return form

    def finish(self, form_list):
        record = form_list[0].save()
        UserAcquirableRelationship.objects.create(
            model=record,
            user=self.request.user)
        messages.success(self.request, _('DNS Record successfully created'))
        return redirect(reverse('supervisr_dns:record-list',
                                kwargs={'zone': self.kwargs.get('zone')}))


class RecordUpdateView(GenericUpdateView):
    """Edit a record"""

    model = Record
    form = RecordForm
    zone = None

    def get_instance(self) -> QuerySet:
        self.zone = get_object_or_404(Zone, domain__domain_name=self.kwargs.get('zone'),
                                      users__in=[self.request.user])
        return self.model.objects.filter(record_zone=self.zone, users__in=[self.request.user],
                                         name=self.kwargs.get('record'),
                                         uuid=self.kwargs.get('uuid'))

    def redirect(self, instance: Record) -> HttpResponse:
        return redirect(reverse('supervisr_dns:record-list',
                                kwargs={'zone': self.kwargs.get('zone')}))

    def update_form(self, form: RecordForm) -> RecordForm:
        # Make a list of all zones so user can switch zones
        user_zones = Zone.objects.filter(users__in=[self.request.user])
        zone_pk = user_zones.filter(domain__domain_name=self.kwargs.get('zone')).first().pk
        form.fields['record_zone'].queryset = user_zones
        form.fields['record_zone'].initial = zone_pk
        return form


class RecordDeleteView(GenericDeleteView):
    """Delete a record"""

    model = Record
    zone = None

    def get_instance(self) -> QuerySet:
        self.zone = get_object_or_404(Zone, domain__domain_name=self.kwargs.get('zone'),
                                      users__in=[self.request.user])
        return self.model.objects.filter(record_zone=self.zone, users__in=[self.request.user],
                                         name=self.kwargs.get('record'),
                                         uuid=self.kwargs.get('uuid'))

    def redirect(self, instance: Record) -> HttpResponse:
        return redirect(reverse('supervisr_dns:record-list',
                                kwargs={'zone': self.kwargs.get('zone')}))
