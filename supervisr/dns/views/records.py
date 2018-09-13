"""Supervisr DNS record views"""
from typing import Union

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import UserAcquirableRelationship
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.records import DataRecordForm, SetRecordForm
from supervisr.dns.models import BaseRecord, DataRecord, SetRecord, Zone


def redirect_back(request: HttpRequest) -> HttpResponse:
    """Redirect back based on URL parameters"""
    if 'zone_uuid' in request.GET:
        return redirect(reverse('supervisr_dns:record-list', kwargs={
            'zone_uuid': request.GET.get('zone_uuid')
        }))
    if 'record_uuid' in request.GET:
        return redirect(reverse('supervisr_dns:record-set-view', kwargs={
            'record_uuid': request.GET.get('record_uuid')
        }))
    if 'back' in request.GET:
        return redirect(request.GET.get('back'))
    return redirect(reverse('supervisr_dns:index'))

class SetRecordView(GenericIndexView):
    """Show list of all sub-records of set"""

    model = BaseRecord
    template = 'dns/records/set_index.html'
    instance = None

    def get_instance(self) -> QuerySet:
        self.instance = get_object_or_404(SetRecord,
                                          uuid=self.kwargs.get('record_uuid'),
                                          users__in=[self.request.user])
        return self.instance.records.filter(users__in=[self.request.user]).order_by('name')

    def update_kwargs(self, kwargs) -> dict:
        kwargs = super().update_kwargs(kwargs)
        kwargs['set'] = self.instance
        return kwargs


# pylint: disable=too-many-ancestors
class DataRecordWizard(BaseWizardView):
    """Wizard to create a new DataRecord"""

    title = _('New Data Record')
    form_list = [DataRecordForm]

    def finish(self, form_list):
        zone = get_object_or_404(Zone,
                                 uuid=self.kwargs.get('zone_uuid'),
                                 users__in=[self.request.user])
        record = form_list[0].save()
        UserAcquirableRelationship.objects.create(
            model=record,
            user=self.request.user)
        messages.success(self.request, _('DNS Record successfully created'))
        if 'zone_uuid' in self.request.GET:
            zone_uuid = self.request.GET.get('zone_uuid')
            zone = get_object_or_404(Zone, uuid=zone_uuid,
                                     users__in=[self.request.user])
            zone.records.add(record)
        return redirect_back(self.request)


# pylint: disable=too-many-ancestors
class SetRecordWizard(BaseWizardView):
    """Wizard to create a new SetRecord"""

    title = _('New Set Record')
    form_list = [SetRecordForm]

    def finish(self, form_list):
        record = form_list[0].save()
        UserAcquirableRelationship.objects.create(
            model=record,
            user=self.request.user)
        messages.success(self.request, _('DNS Record successfully created'))
        if 'zone_uuid' in self.request.GET:
            zone_uuid = self.request.GET.get('zone_uuid')
            zone = get_object_or_404(Zone, uuid=zone_uuid,
                                     users__in=[self.request.user])
            zone.records.add(record)
        return redirect_back(self.request)


class RecordUpdateView(GenericUpdateView):
    """Edit a record"""

    model = BaseRecord
    form = DataRecordForm
    zone = None

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         uuid=self.kwargs.get('record_uuid'))

    def redirect(self, instance: DataRecord) -> HttpResponse:
        return redirect_back(self.request)

    def get_form(self, *args, instance: BaseRecord, **kwargs
                ) -> Union[DataRecordForm, SetRecordForm]:
        instance = instance.cast()
        if isinstance(instance, DataRecord):
            return DataRecordForm(*args, instance=instance, **kwargs)
        elif isinstance(instance, SetRecord):
            return SetRecordForm(*args, instance=instance, **kwargs)
        raise ValueError('instance must be either DataRecord or SetRecord')


class RecordDeleteView(GenericDeleteView):
    """Delete a record"""

    model = BaseRecord
    zone = None

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         uuid=self.kwargs.get('record_uuid'))

    def redirect(self, instance: DataRecord) -> HttpResponse:
        return redirect_back(self.request)
