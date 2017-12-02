"""
Supervisr Mail Account Views
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import Event, UserProductRelationship
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.account import (MailAccountForm,
                                          MailAccountFormAlias,
                                          MailAccountFormCredentials,
                                          MailAccountGeneralForm)
from supervisr.mail.models import MailAccount, MailAlias, MailDomain

LOGGER = logging.getLogger(__name__)


@login_required
def index(req):
    """
    Account Index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    acc_accounts = MailAccount.objects \
        .filter(domain__in=domains, users__in=[req.user]) \
        .order_by('domain', 'address')

    paginator = Paginator(acc_accounts, req.user.rows_per_page)

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
    form_list = [MailAccountGeneralForm, MailAccountFormCredentials, MailAccountFormAlias]
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
        domain = form_dict['0'].cleaned_data.get('domain')
        m_acc = MailAccount.objects.create(
            name="Mail Account %s" % form_dict['0'].cleaned_data.get('address'),
            address=form_dict['0'].cleaned_data.get('address'),
            domain=domain,
            can_send=form_dict['0'].cleaned_data.get('can_send'),
            can_receive=form_dict['0'].cleaned_data.get('can_receive'),
            is_catchall=form_dict['0'].cleaned_data.get('is_catchall'),
            )
        m_acc.set_password(self.request.user, form_dict['1'].cleaned_data.get('password'))
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
        return redirect(reverse('supervisr/mail:mail-domain-view', kwargs=
                                {'domain': form_dict['0'].cleaned_data.get('domain').domain}))

@login_required
def account_set_password(req, domain, account):
    """
    Set password for account
    """
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[req.user])
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    accounts = MailAccount.objects.filter(domain=r_domain, address=account, users__in=[req.user])
    if not accounts.exists():
        raise Http404
    r_account = accounts.first()

    if req.method == 'POST':

        form = MailAccountFormCredentials(req.POST)
        form.fields['password'].required = True
        form.fields['password_rep'].required = True

        if form.is_valid():
            r_account.set_password(req.user, form.cleaned_data.get('password'), request=req)
            r_account.save()

            messages.success(req, _('Successfully set password for %(account)s' \
                             % {'account': r_account.email}))
            Event.create(
                user=req.user,
                message=_('You reset the password for %(account)s' % {'account': r_account.email}),
                request=req,
                current=False)
            LOGGER.info("Updated password for %s", r_account.email)
            return redirect(reverse('supervisr/mail:mail-domain-view', kwargs={'domain': domain}))

    else:

        form = MailAccountFormCredentials()
        form.fields['password'].required = True
        form.fields['password_rep'].required = True

    return render(req, 'core/generic_form_modal.html', {
        'form': form,
        'title': _('Change password for %(account)s' % {'account': r_account.email})
        })

@login_required
# pylint: disable=unused-argument
def account_edit(req, domain, account):
    """
    Show view to edit account
    """
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[req.user])
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    accounts = MailAccount.objects.filter(domain=r_domain, users__in=[req.user], address=account)
    if not accounts.exists():
        raise Http404
    r_account = accounts.first()

    # Make a list of all zones so user can switch zones
    user_domains = MailDomain.objects.filter(users__in=[req.user])
    domain_pk = user_domains.filter(domain__domain=domain).first().pk
    full_address = '%s@%s' % (r_account.address, r_domain.domain.domain)

    if req.method == 'POST':
        form = MailAccountForm(req.POST, instance=r_account)
        form.fields['domain'].queryset = user_domains
        form.fields['domain'].initial = domain_pk
        if form.is_valid():
            r_account.save()
            messages.success(req, _('Successfully edited Account'))
            return redirect(reverse('supervisr/mail:mail-domain-view', kwargs={'domain': domain}))
        messages.error(req, _("Invalid Account"))
        return redirect(reverse('supervisr/mail:mail-domain-view', kwargs={'domain': domain}))
    else:
        form = MailAccountForm(instance=r_account)
        form.fields['domain'].queryset = user_domains
        form.fields['domain'].initial = domain_pk
    return render(req, 'core/generic_form_modal.html', {
        'form': form,
        'primary_action': 'Save',
        'title': _('Edit Account %(address)s' % {'address': full_address}),
        'size': 'lg',
        })

@login_required
# pylint: disable=unused-argument
def account_delete(req, domain, account):
    """
    Show view to delete account
    """
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[req.user])
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    accounts = MailAccount.objects.filter(domain=r_domain, address=account, users__in=[req.user])
    if not accounts.exists():
        raise Http404
    r_account = accounts.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_account.delete()
        messages.success(req, _('Account successfully deleted'))
        return redirect(reverse('supervisr/mail:mail-domain-view', kwargs={'domain': domain}))

    return render(req, 'core/generic_delete.html', {
        'object': 'Account %s' % r_account.email_raw,
        'delete_url': reverse('supervisr/mail:mail-account-delete', kwargs={
            'domain': r_domain.domain.domain,
            'account': r_account.address
            })
        })
