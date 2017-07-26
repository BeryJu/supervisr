"""
Supervisr DNS Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import BaseProvider
from supervisr.core.views.wizard import BaseWizardView
from supervisr.dns.forms.zone import ZoneForm
from supervisr.dns.models import Zone


@login_required
def index(req):
    """
    Show list of users zones
    """
    all_domains = Domain.objects.filter(users__in=[req.user])
    dns_domains = Zone.objects.filter(domain__in=all_domains).order_by('domain__domain')

    paginator = Paginator(dns_domains, max(int(req.GET.get('per_page', 50)), 1))

    page = req.GET.get('page')
    try:
        zones = paginator.page(page)
    except PageNotAnInteger:
        zones = paginator.page(1)
    except EmptyPage:
        zones = paginator.page(paginator.num_pages)

    return render(req, 'dns/zone/index.html', {
        'zones': zones
        })

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

            providers = BaseProvider.get_providers(filter_sub=['dns_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                userproductrelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['provider'].queryset = provider_instance
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        m_dom = Zone.objects.create(
            domain=form_dict['0'].cleaned_data.get('domain'),
            provider=form_dict['0'].cleaned_data.get('provider'),
            enabled=form_dict['0'].cleaned_data.get('enabled'))
        UserProductRelationship.objects.create(
            product=m_dom,
            user=self.request.user)
        messages.success(self.request, _('DNS Domain successfully created'))
        return redirect(reverse('supervisr/dns:dns-domains'))

@login_required
def edit(req, domain):
    """
    Edit a domain
    """
    domains = Zone.objects.filter(name=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()
    if req.method == 'POST':
        form = ZoneForm(req.POST)

        if form.is_valid():
            r_domain.name = form.cleaned_data.get('name')
            r_domain.type = form.cleaned_data.get('type')
            r_domain.master = form.cleaned_data.get('master')
            r_domain.account = form.cleaned_data.get('account')
            r_domain.save()
            messages.success(req, _('Successfully added Domain'))
            return redirect(reverse('domains-overview'))
        messages.error(req, _("Invalid Domain"))
        return redirect(reverse('domains-overview'))
    else:
        form = ZoneForm(initial={
            'name': r_domain.name,
            'type': r_domain.type,
            'master': r_domain.master,
            'account': r_domain.account,
            })

    return render(req, 'core/generic_form.html', {
        'form': form,
        'primary_action': 'Edit',
        'title': 'Domains Edit'
        })

@login_required
def delete(req, domain):
    """
    Delete a domain
    """
    domains = Zone.objects.filter(name=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()
    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_domain.delete()
        messages.success(req, _('Domain successfully deleted'))
        return redirect(reverse('domains-overview'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Domain %s' % domains.first().name,
        'delete_url': reverse('domains-delete', kwargs={'domain': r_domain.name})
        })
