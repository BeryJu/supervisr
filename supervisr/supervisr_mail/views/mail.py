"""
Supervisr Mail Common Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.models import UserProductRelationship
from supervisr.utils import do_404
from supervisr.views.wizard import BaseWizardView

from ..forms.mail_account import (MailAccountForm, MailAccountFormCredentials,
                                  MailAccountFormForwarder)
from ..models import MailAccount, MailDomain


@login_required
def index(req):
    """
    Mail index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    return render(req, 'mail/index.html', {'domains': domains})

@login_required
def accounts(req):
    """
    Mail Account Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    mail_accounts = MailAccount.objects \
        .filter(domain_mail__in=domains, users__in=[req.user]) \
        .order_by('domain_mail')
    return render(req, 'mail/account-index.html', {'accounts': mail_accounts})

@login_required
def accounts_view(req, domain, account):
    """
    View a Mail Account
    """
    # Check if domain exists first
    m_domain = MailDomain.objects.filter(domain=domain)
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

    def done(self, form_dict, **kwargs):
        m_acc = MailAccount.objects.create(
            address=form_dict['0'].cleaned_data.get('address'),
            domain_mail=form_dict['0'].cleaned_data.get('domain'),
            can_send=form_dict['0'].cleaned_data.get('can_send'),
            can_receive=form_dict['0'].cleaned_data.get('can_receive'),
            is_catchall=form_dict['0'].cleaned_data.get('is_catchall'),
            price=0,
            password=form_dict['1'].cleaned_data.get('password'),
            )
        UserProductRelationship.objects.create(
            product=m_acc,
            user=self.request.user
            )
        return redirect(reverse('supervisr_mail:mail-accounts'))
