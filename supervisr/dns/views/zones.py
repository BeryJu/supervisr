"""
Supervisr DNS Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import Zone


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Show list of users zones"""
    all_domains = Domain.objects.filter(users__in=[request.user])
    dns_domains = Zone.objects.filter(domain__in=all_domains).order_by('domain__domain')

    paginator = Paginator(dns_domains, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        zones = paginator.page(page)
    except PageNotAnInteger:
        zones = paginator.page(1)
    except EmptyPage:
        zones = paginator.page(paginator.num_pages)

    return render(request, 'dns/zones/index.html', {
        'zones': zones
        })

# pylint: disable=too-many-ancestors
class ZoneNewView(BaseWizardView):
    """Wizard to create a blank Zone"""

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

            providers = get_providers(filter_sub=['dns_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                userproductrelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['provider'].queryset = provider_instance
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        zone = form_dict['0'].save(commit=False)
        zone.save()
        UserProductRelationship.objects.create(
            product=zone,
            user=self.request.user)
        messages.success(self.request, _('DNS Domain successfully created'))
        return redirect(reverse('supervisr/dns:dns-index'))

@login_required
def edit(request: HttpRequest, zone: str) -> HttpResponse:
    """Edit a zone"""
    # Check if zone exists before doing anything else
    zones = Zone.objects.filter(domain__domain=zone, users__in=[request.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()
    # Create list of all possible provider instances
    providers = get_providers(filter_sub=['dns_provider'], path=True)
    provider_instance = ProviderInstance.objects.filter(
        provider_path__in=providers,
        userproductrelationship__user__in=[request.user])

    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=r_zone)
        form.fields['provider'].queryset = provider_instance
        if form.is_valid():
            form.save()
            messages.success(request, _('Successfully edited Zone'))
            return redirect(reverse('supervisr/dns:dns-index'))
    else:
        form = ZoneForm(instance=r_zone)
        form.fields['provider'].queryset = provider_instance
    return render(request, 'core/generic_form_modal.html', {
        'form': form,
        'primary_action': 'Save',
        'title': 'Zone Edit'
        })

@login_required
def delete(request: HttpRequest, zone: str) -> HttpResponse:
    """Delete a zone"""
    # Check if zone exists before doing anything else
    zones = Zone.objects.filter(domain__domain=zone, users__in=[request.user])
    if not zones.exists():
        raise Http404
    r_zone = zones.first()

    if request.method == 'POST' and 'confirmdelete' in request.POST:
        # User confirmed deletion
        r_zone.delete()
        messages.success(request, _('Zone successfully deleted'))
        return redirect(reverse('supervisr/dns:dns-index'))

    return render(request, 'core/generic_delete.html', {
        'object': 'Zone %s' % r_zone.domain,
        'delete_url': reverse('supervisr/dns:dns-zone-delete', kwargs={'zone': r_zone.domain})
        })
