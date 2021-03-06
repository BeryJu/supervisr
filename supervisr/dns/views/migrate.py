"""Supervisr DNS Migration views"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.wizards import BaseWizardView
from supervisr.dns.forms.migrate import ZoneImportForm, ZoneImportPreviewForm
from supervisr.dns.forms.zones import ZoneForm
from supervisr.dns.models import Zone
from supervisr.dns.utils import import_bind

TEMPLATES = {
    '0': 'generic/wizard.html',
    '1': 'generic/wizard.html',
    '2': 'dns/migrate/preview.html',
}


# pylint: disable=too-many-ancestors
class BindZoneImportWizard(LoginRequiredMixin, BaseWizardView):
    """Import DNS records from bind zone"""

    title = _('Import Bind Zone')
    form_list = [ZoneForm, ZoneImportForm, ZoneImportPreviewForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(BindZoneImportWizard, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            # This step should be seperated into the DomainNewWizard, which should run before this
            domains = Zone.objects.filter(users__in=[self.request.user])

            unused_domains = Domain.objects.filter(users__in=[self.request.user]) \
                .exclude(pk__in=domains.values_list('domain', flat=True))

            providers = get_providers(capabilities=['dns'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['providers'].queryset = provider_instance
        elif step == '2':
            if '1-zone_data' in self.request.POST:
                form.records = import_bind(self.request.POST['1-zone_data'])
        return form

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def finish(self, zone_form, zone_data_form, accept_form):
        if accept_form.cleaned_data.get('accept'):
            records = import_bind(zone_data_form.cleaned_data.get('zone_data'),
                                  root_zone=zone_form.cleaned_data.get('domain').domain)
            m_dom = Zone.objects.create(
                name=zone_form.cleaned_data.get('domain'),
                domain=zone_form.cleaned_data.get('domain'),
                provider=zone_form.cleaned_data.get('provider'),
                enabled=zone_form.cleaned_data.get('enabled'))
            UserAcquirableRelationship.objects.create(
                model=m_dom,
                user=self.request.user)
            for rec in records:
                rec.domain = m_dom
                rec.save()
                UserAcquirableRelationship.objects.create(
                    model=rec,
                    user=self.request.user)
            messages.success(self.request, _('DNS domain successfully created and '
                                             '%(count)d records imported.' % {
                                                 'count': len(records)}))
            return redirect(reverse('supervisr_dns:dns-record-list',
                                    kwargs={'uuid': m_dom.uuid}))
        messages.error(self.request, _('Created nothing'))
        return redirect(reverse('supervisr_dns:index'))
