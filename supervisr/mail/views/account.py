"""
Supervisr Mail Account Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import UserProductRelationship
from supervisr.core.views.wizard import BaseWizardView
from supervisr.mail.forms.account import (MailAccountForm,
                                          MailAccountFormAlias,
                                          MailAccountFormCredentials)
from supervisr.mail.models import MailAccount, MailAlias, MailDomain


@login_required
def index(req):
    """
    Account Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    acc_accounts = MailAccount.objects \
        .filter(domain__in=domains, users__in=[req.user]) \
        .order_by('domain', 'address')

    paginator = Paginator(acc_accounts, int(req.GET.get('per_page', 50)))

    page = req.GET.get('page')
    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = paginator.page(paginator.num_pages)

    return render(req, 'mail/account/index.html', {
        'acc_accounts': accounts,
        })

@staticmethod
def check_cred_form(wizard):
    """
    if can_send is true, ask for creds
    """
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('can_send', True)

# pylint: disable=too-many-ancestors
class AccountNewView(BaseWizardView):
    """
    Wizard to create a Mail Account
    """

    title = _('New Mail Account')
    form_list = [MailAccountForm, MailAccountFormCredentials, MailAccountFormAlias]
    condition_dict = {
        '1': check_cred_form
    }

    def get_form(self, step=None, data=None, files=None):
        form = super(AccountNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            form.fields['domain'].queryset = \
                MailDomain.objects.filter(users__in=[self.request.user])
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        m_acc = MailAccount.objects.create(
            address=form_dict['0'].cleaned_data.get('address'),
            domain=form_dict['0'].cleaned_data.get('domain'),
            can_send=form_dict['0'].cleaned_data.get('can_send'),
            can_receive=form_dict['0'].cleaned_data.get('can_receive'),
            is_catchall=form_dict['0'].cleaned_data.get('is_catchall'),
            )
        m_acc.set_password(form_dict['1'].cleaned_data.get('password'))
        UserProductRelationship.objects.create(
            product=m_acc,
            user=self.request.user
            )
        if form_dict['2'].cleaned_data.get('alias_dest') != []:
            for alias_dest in form_dict['2'].cleaned_data.get('alias_dest'):
                MailAlias.objects.create(
                    account=m_acc,
                    destination=alias_dest
                    )
        messages.success(self.request, _('Mail Account successfully created'))
        return redirect(reverse('supervisr/mail:mail-index'))

@login_required
# pylint: disable=unused-argument
def account_edit(req, domain, account):
    """
    Show view to edit account
    """
    pass

@login_required
# pylint: disable=unused-argument
def account_delete(req, domain, account):
    """
    Show view to delete account
    """
    domains = MailDomain.objects.filter(domain__domain=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    accounts = MailAccount.objects.filter(domain=r_domain, address=account)
    if not accounts.exists():
        raise Http404
    r_account = accounts.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_account.delete()
        messages.success(req, _('Account successfully deleted'))
        return redirect(reverse('supervisr/mail:mail-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Account %s' % r_account.email_raw,
        'delete_url': reverse('supervisr/mail:mail-account-delete', kwargs={
            'domain': r_domain.domain.domain,
            'account': r_account.address
            })
        })
