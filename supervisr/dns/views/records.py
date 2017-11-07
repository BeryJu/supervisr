"""
Supervisr DNS record views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import UserProductRelationship
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.records import RecordForm
from supervisr.dns.models import Record, Zone


@login_required
def list_records(req, zone):
    """
    Show list of records for zone
    """
    # check if zone exists
    zones = Zone.objects.filter(domain__domain=zone, users__in=[req.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()
    # get all records for the zone
    all_records = Record.objects.filter(domain=r_zone, users__in=[req.user]).order_by('name')

    paginator = Paginator(all_records, max(int(req.GET.get('per_page', 50)), 1))

    page = req.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    return render(req, 'dns/records/index.html', {
        'records': records,
        'zone': r_zone,
        })

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
            zone_pk = user_zones.filter(domain__domain=self.kwargs['zone']).first().pk
            form.fields['domain'].queryset = user_zones
            form.fields['domain'].initial = zone_pk
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        record = form_dict['0'].save(commit=False)
        record.save()
        UserProductRelationship.objects.create(
            product=record,
            user=self.request.user)
        messages.success(self.request, _('DNS Record successfully created'))
        return redirect(reverse('supervisr/dns:dns-record-list',
                                kwargs={'zone': self.kwargs['zone']}))

@login_required
def edit(req, zone, record, uuid):
    """
    Edit a record
    """
    # Check if zone exists before doing anything else
    zones = Zone.objects.filter(domain__domain=zone, users__in=[req.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()
    # Check if the record exists too
    records = Record.objects.filter(domain=r_zone, users__in=[req.user], name=record, uuid=uuid)
    if not records.exists():
        raise Http404
    assert len(records) == 1
    r_record = records.first()

    # Make a list of all zones so user can switch zones
    user_zones = Zone.objects.filter(users__in=[req.user])
    zone_pk = user_zones.filter(domain__domain=zone).first().pk

    if req.method == 'POST':
        form = RecordForm(req.POST, instance=r_record)
        form.fields['domain'].queryset = user_zones
        form.fields['domain'].initial = zone_pk
        if form.is_valid():
            r_record.save()
            messages.success(req, _('Successfully edited Record'))
            return redirect(reverse('supervisr/dns:dns-record-list', kwargs={'zone': zone}))
        messages.error(req, _("Invalid Record"))
    else:
        form = RecordForm(instance=r_record)
        form.fields['domain'].queryset = user_zones
        form.fields['domain'].initial = zone_pk
    return render(req, 'core/generic_form_modal.html', {
        'form': form,
        'primary_action': 'Save',
        'title': 'Record Edit',
        'size': 'lg',
        })

@login_required
def delete(req, zone, record, uuid):
    """
    Delete a record
    """
    # Check if zone exists before doing anything else
    zones = Zone.objects.filter(domain__domain=zone, users__in=[req.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()

    records = Record.objects.filter(domain=r_zone, users__in=[req.user], name=record, uuid=uuid)
    if not records.exists():
        raise Http404
    assert len(records) == 1
    r_record = records.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_record.delete()
        messages.success(req, _('Record successfully deleted'))
        return redirect(reverse('supervisr/dns:dns-record-list', kwargs={'zone': zone}))

    return render(req, 'core/generic_delete.html', {
        'object': 'Record %s' % r_record.name,
        'delete_url': reverse('supervisr/dns:dns-record-delete', kwargs={
            'zone': zone,
            'record': record,
            'uuid': r_record.uuid,
            })
        })
