"""
Supervisr Mail Alias Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.alias import MailAliasForm
from supervisr.mail.models import MailAccount, MailAlias, MailDomain


@login_required
def index(req):
    """
    Index of aliases
    """
    domains = MailDomain.objects.filter(users__in=[req.user])
    fwd_accounts = MailAlias.objects \
        .filter(account__domain__in=domains, account__users__in=[req.user]) \
        .order_by('account__domain', 'account__address')
    paginator = Paginator(fwd_accounts, max(int(req.GET.get('per_page', 50)), 1))

    page = req.GET.get('page')
    try:
        aliases = paginator.page(page)
    except PageNotAnInteger:
        aliases = paginator.page(1)
    except EmptyPage:
        aliases = paginator.page(paginator.num_pages)

    return render(req, 'mail/alias/index.html', {
        'fwd_accounts': aliases,
        })

# pylint: disable=too-many-ancestors
class AliasNewView(BaseWizardView):
    """
    Wizard to create a Mail Alias
    """

    title = _('New Mail Alias')
    form_list = [MailAliasForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(AliasNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            domains = MailDomain.objects.filter(users__in=[self.request.user])
            form.fields['accounts'].queryset = \
                MailAccount.objects \
                    .filter(domain__in=domains, users__in=[self.request.user]) \
                    .order_by('domain', 'address')
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        m_acc = form_dict['0'].cleaned_data.get('accounts')
        if form_dict['0'].cleaned_data.get('alias_dest') != []:
            for alias_dest in form_dict['0'].cleaned_data.get('alias_dest'):
                MailAlias.objects.create(
                    account=m_acc,
                    destination=alias_dest
                    )
        messages.success(self.request, _('Mail Aliases successfully created'))
        return redirect(reverse('supervisr/mail:mail-alias-index'))

@login_required
# pylint: disable=unused-argument
def alias_delete(req, domain, dest):
    """
    Show view to delete alias
    """
    domains = MailDomain.objects.filter(domain__domain=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    aliases = MailAlias.objects.filter(account__domain=r_domain, destination=dest)
    if not aliases.exists():
        raise Http404
    r_alias = aliases.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_alias.delete()
        messages.success(req, _('Alias successfully deleted'))
        return redirect(reverse('supervisr/mail:mail-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Alias %s' % r_alias.destination,
        'delete_url': reverse('supervisr/mail:mail-alias-delete', kwargs={
            'domain': r_domain.domain.domain,
            'dest': r_alias.destination
            })
        })
