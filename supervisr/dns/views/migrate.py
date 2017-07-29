"""
Supervisr DNS Migration views
"""

from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import BaseProvider
from supervisr.core.views.wizard import BaseWizardView
from supervisr.dns.forms.domain import DNSDomainForm
from supervisr.dns.forms.migrate import ZoneImportForm, ZoneImportPreviewForm
from supervisr.dns.models import DNSDomain
from supervisr.dns.utils import zone_to_rec

TEMPLATES = {
    '0': 'core/generic_wizard.html',
    '1': 'core/generic_wizard.html',
    '2': 'dns/migrate/preview.html',
}

# pylint: disable=too-many-ancestors
class BindZoneImportWizard(BaseWizardView):
    """
    Import DNS records from bind zone
    """

    title = _('Import Bind Zone')
    form_list = [DNSDomainForm, ZoneImportForm, ZoneImportPreviewForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(BindZoneImportWizard, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            # This step should be seperated into the DomainNewWizard, which should run before this
            domains = DNSDomain.objects.filter(users__in=[self.request.user])

            unused_domains = Domain.objects.filter(users__in=[self.request.user]) \
                .exclude(pk__in=domains.values_list('domain', flat=True))

            providers = BaseProvider.get_providers(filter_sub=['dns_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                userproductrelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['provider'].queryset = provider_instance
        elif step == '2':
            if '1-zone_data' in self.request.POST:
                form.records = zone_to_rec(self.request.POST['1-zone_data'])
        return form

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        if form_dict['2'].cleaned_data.get('accept'):
            records = zone_to_rec(form_dict['1'].cleaned_data.get('zone_data'))
            m_dom = DNSDomain.objects.create(
                domain=form_dict['0'].cleaned_data.get('domain'),
                provider=form_dict['0'].cleaned_data.get('provider'))
            UserProductRelationship.objects.create(
                product=m_dom,
                user=self.request.user)
            for rec in records:
                rec.domain = m_dom
                rec.save()
            messages.success(self.request, _('DNS Domain successfully created and '
                                             '%(count)d Records imported.' % {
                                                 'count': len(records)}))
        else:
            messages.error(self.request, _('Not created nuthin'))
        return redirect(reverse('supervisr/dns:dns-domains'))
