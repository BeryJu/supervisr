"""
Supervisr Mail Common Views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from supervisr.models import UserProductRelationship
from supervisr.utils import do_404

from ..forms.mail_account import MailAccountForm
from ..models import MailAccount, MailDomain


@login_required
def index(req):
    """
    Mail index
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    return render(req, 'mail/index.html', {'domains': domains})

@login_required
def view(req, domain, account):
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

@login_required
def accounts(req):
    """
    werqw
    """

    domains = MailDomain.objects.filter(users__in=[req.user])
    form = MailAccountForm(initial={'kind': MailAccountForm.KIND_NORMAL})
    form.fields['domain'].queryset = domains
    return render(req, 'mail/accounts.html', {'form': form})

# New Mail Account - Data to be gathered
#  - Check if they have a MailDomain yet, otherwise redirect back
#  - Address with dropdown for domain
#  - Kind (Nornal, Send only, Receive only, Forwarder)
#  - credentials if not forwarder
#  - forwarder destination (optional if not forwader)
#  - mailbox plan (quota, etc) (if not forwarder)
# @login_required
# def new_step_1(req):
#     if req.method == 'GET':
#         form = NewMailAccountStep1Form()
#     elif req.method == 'POST':
#         form = NewMailAccountStep1Form(req.POST)
#         if form.is_valid():
#             ma = form.save()
#             messages.success(req, _('Mail Account successfully added'))
#     return render(req, 'core/generic_form.html', {
#         'title': _('New Mail account'),
#         'primary_action': _('Next'),
#         'form': form
#         })
