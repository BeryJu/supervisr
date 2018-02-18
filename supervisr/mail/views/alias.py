"""
Supervisr Mail Alias Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.views.generic import GenericDeleteView, GenericUpdateView
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.alias import MailAliasForm, MailAliasWizardForm
from supervisr.mail.models import MailAccount, MailAlias, MailDomain


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Index of aliases"""
    domains = MailDomain.objects.filter(users__in=[request.user])
    fwd_accounts = MailAlias.objects \
        .filter(account__domain__in=domains, account__users__in=[request.user]) \
        .order_by('account__domain', 'account__address')
    paginator = Paginator(fwd_accounts, request.user.rows_per_page)

    page = request.GET.get('page')
    try:
        aliases = paginator.page(page)
    except PageNotAnInteger:
        aliases = paginator.page(1)
    except EmptyPage:
        aliases = paginator.page(paginator.num_pages)

    return render(request, 'mail/alias/index.html', {
        'fwd_accounts': aliases,
        })

# pylint: disable=too-many-ancestors
class AliasNewView(BaseWizardView):
    """Wizard to create a Mail Alias"""

    title = _('New Mail Alias')
    form_list = [MailAliasWizardForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(AliasNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            form.request = self.request
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        source = form_dict['0'].cleaned_data.get('source')
        _source_local, _source_domain = source.split('@')
        # Get Domain and matching accounts
        source_domain = MailDomain.objects.get(domain__domain=_source_domain)
        source_accounts = MailAccount.objects.filter(domain=source_domain, address=_source_local)
        # Check if source account exists, or create it if not
        if not source_accounts.exists():
            source_account = MailAccount.objects.create(address=_source_local, domain=source_domain)
            source_domain.copy_upr_to(source_account)
        else:
            source_account = source_accounts.first()

        amount = 0
        for destination in form_dict['0'].cleaned_data.get('destination'):
            MailAlias.objects.create(account=source_account, destination=destination)
            amount += 1

        messages.success(self.request, _('Successfully created %(amount)d aliases.' % {
            'amount': amount
        }))
        return redirect(reverse('supervisr_mail:mail-domain-view',
                                kwargs={'domain': source_domain.domain.domain})+'#clr_tab=aliases')


class MailAliasUpdateView(GenericUpdateView):
    """Update MailAlias"""

    model = MailAlias
    form = MailAliasForm

    def redirect(self, instance: MailAlias) -> HttpResponse:
        domain = get_object_or_404(MailDomain, domain__domain=self.kwargs.get('domain'),
                                   users__in=[self.request.user])
        return redirect(reverse('supervisr_mail:mail-domain-view',
                                kwargs={'domain': domain})+'#clr_tab=aliases')

    def get_instance(self) -> QuerySet:
        """Get Alias from name"""
        domain = get_object_or_404(MailDomain, domain__domain=self.kwargs.get('domain'),
                                   users__in=[self.request.user])
        return self.model.objects.filter(account__domain=domain,
                                         destination=self.kwargs.get('dest'),
                                         account__users__in=[self.request.user])

class MailAliasDeleteView(GenericDeleteView):
    """Delete MailAlias"""

    model = MailAlias

    def redirect(self, instance: MailAlias) -> HttpResponse:
        domain = get_object_or_404(MailDomain, domain__domain=self.kwargs.get('domain'),
                                   users__in=[self.request.user])
        return redirect(reverse('supervisr_mail:mail-domain-view',
                                kwargs={'domain': domain})+'#clr_tab=aliases')

    def get_instance(self) -> QuerySet:
        """Get Alias from name"""
        domain = get_object_or_404(MailDomain, domain__domain=self.kwargs.get('domain'),
                                   users__in=[self.request.user])
        return self.model.objects.filter(account__domain=domain,
                                         destination=self.kwargs.get('dest'),
                                         account__users__in=[self.request.user])
