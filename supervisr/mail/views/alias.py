"""
Supervisr Mail Alias Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext as _

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
        return redirect(reverse('supervisr_mail:mail-domain-view',
                                kwargs={'domain': m_acc.domain.domain})+'#clr_tab=aliases')

@login_required
def alias_edit(request: HttpRequest, domain: str, dest: str) -> HttpResponse:
    """Edit Alias"""
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[request.user])
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    aliases = MailAlias.objects.filter(account__domain=r_domain,
                                       destination=dest, account__users__in=[request.user])
    if not aliases.exists():
        raise Http404
    r_alias = aliases.first()

    if request.method == 'POST':
        form = MailAliasForm(request.POST, instance=r_alias)
        if form.is_valid():
            form.save()
            messages.success(request, _('Successfully updated Alias'))
            return redirect(reverse('supervisr_mail:mail-domain-view',
                                    kwargs={'domain': domain})+'#clr_tab=aliases')
    else:
        form = MailAliasForm(instance=r_alias)

    return render(request, 'core/generic_form_modal.html', {
        'form': form,
        'primary_action': 'Save',
        'title': 'Alias Edit',
        'size': 'lg',
        })

@login_required
def alias_delete(request: HttpRequest, domain: str, dest: str) -> HttpResponse:
    """Show view to delete alias"""
    domains = MailDomain.objects.filter(domain__domain=domain, users__in=[request.user])
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    aliases = MailAlias.objects.filter(account__domain=r_domain,
                                       destination=dest, account__users__in=[request.user])
    if not aliases.exists():
        raise Http404
    r_alias = aliases.first()

    if request.method == 'POST' and 'confirmdelete' in request.POST:
        # User confirmed deletion
        r_alias.delete()
        messages.success(request, _('Alias successfully deleted'))
        return redirect(reverse('supervisr_mail:mail-domain-view',
                                kwargs={'domain': domain})+'#clr_tab=aliases')

    return render(request, 'core/generic_delete.html', {
        'object': 'Alias %s' % r_alias.destination,
        'delete_url': reverse('supervisr_mail:mail-alias-delete', kwargs={
            'domain': r_domain.domain.domain,
            'dest': r_alias.destination
            })
        })
