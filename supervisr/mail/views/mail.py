"""
Supervisr Mail Common Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import UserProductRelationship
from supervisr.core.utils import do_404
from supervisr.core.views.wizard import BaseWizardView

from ..forms.mail_account import (MailAccountForm, MailAccountFormCredentials,
                                  MailAccountFormForwarder)
from ..models import MailAccount, MailDomain, MailForwarder


@login_required
def index(req):
    """
    Mail Domain Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    all_accounts = MailAccount.objects \
        .filter(domain__in=domains, users__in=[req.user]) \
        .order_by('domain')
    acc_accounts = all_accounts.filter(mailforwarder__isnull=True)
    fwd_accounts = all_accounts.filter(mailforwarder__isnull=False)

    return render(req, 'mail/recipient-index.html', {
        'acc_accounts': acc_accounts,
        'fwd_accounts': fwd_accounts,
        })

@login_required
def accounts(req):
    """
    Mail Account Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    mail_accounts = MailAccount.objects \
        .filter(domain__in=domains, users__in=[req.user]) \
        .order_by('domain')
    return render(req, 'mail/account-index.html', {'accounts': mail_accounts})

@login_required
def accounts_view(req, domain, account):
    """
    View a Mail Account
    """
    # Check if domain exists first
    m_domain = MailDomain.objects.filter(domain__domain=domain)
    if m_domain.exists() is False:
        return do_404(req, message='Account not found')
    # Check if account exists
    m_account = MailAccount.objects.filter(
        domain=m_domain.first(),
        address=account)
    if m_account.exists() is False:
        return do_404(req, message='Account not found')
    # Check if the current user has access
    m_upr = UserProductRelationship.objects.filter(
        user=req.user,
        product=m_account.first())
    if m_upr.exists() is False:
        return do_404(req, message='Account not found')
    return render(req, 'mail/view.html', {'account': m_account})

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
    form_list = [MailAccountForm, MailAccountFormCredentials, MailAccountFormForwarder]
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
        if form_dict['2'].cleaned_data.get('forwarder_dest') != '':
            MailForwarder.objects.create(
                account=m_acc,
                destination=form_dict['2'].cleaned_data.get('forwarder_dest')
                )
        messages.success(self.request, _('Mail Account successfully created'))
        return redirect(reverse('mail:mail-index'))

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
        return redirect(reverse('mail:mail-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Account %s' % r_account.email_raw,
        'delete_url': reverse('mail:mail-account-delete', kwargs={
            'domain': r_domain.name,
            'account': r_account.address
            })
        })
