"""
Supervisr Mail Domain Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.domain import MailDomainForm
from supervisr.mail.models import MailAccount, MailAlias, MailDomain


@login_required
def view(req, domain):
    """
    Show details to a domain
    """
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[req.user])

    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    acc_accounts = MailAccount.objects \
        .filter(domain=r_domain, users__in=[req.user]) \
        .order_by('address')

    acc_paginator = Paginator(acc_accounts, req.user.rows_per_page)
    page = req.GET.get('accountPage')
    try:
        accounts = acc_paginator.page(page)
    except PageNotAnInteger:
        accounts = acc_paginator.page(1)
    except EmptyPage:
        accounts = acc_paginator.page(acc_paginator.num_pages)

    fwd_accounts = MailAlias.objects \
        .filter(account__domain=r_domain, account__users__in=[req.user]) \
        .order_by('account__domain', 'account__address')
    ali_paginator = Paginator(fwd_accounts, req.user.rows_per_page)

    page = req.GET.get('aliasPage')
    try:
        aliases = ali_paginator.page(page)
    except PageNotAnInteger:
        aliases = ali_paginator.page(1)
    except EmptyPage:
        aliases = ali_paginator.page(ali_paginator.num_pages)

    return render(req, 'mail/domain/view.html', {
        'domain': r_domain,
        'acc_accounts': accounts,
        'acc_aliases': aliases,
        'title': '%s - Domains' % r_domain.domain.domain,
        })

# pylint: disable=too-many-ancestors
class DomainNewView(BaseWizardView):
    """
    Wizard to create a Mail Domain
    """

    title = _('New Mail Domain')
    form_list = [MailDomainForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(DomainNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            domains = MailDomain.objects.filter(users__in=[self.request.user])

            unused_domains = Domain.objects.filter(users__in=[self.request.user]) \
                .exclude(pk__in=domains.values_list('domain', flat=True))

            providers = get_providers(filter_sub=['mail_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                userproductrelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['provider'].queryset = provider_instance
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        m_dom = form_dict['0'].save()
        UserProductRelationship.objects.create(
            product=m_dom,
            user=self.request.user)
        messages.success(self.request, _('Mail Domain successfully created'))
        return redirect(reverse('supervisr/mail:mail-index'))
