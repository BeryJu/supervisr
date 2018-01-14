"""
Supervisr Core Domain Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.domains import DomainForm
from supervisr.core.models import (Domain, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.wizards import BaseWizardView


@login_required
def index(request):
    """Show a n overview over all domains"""
    user_domains = Domain.objects.filter(
        users__in=[request.user])
    return render(request, 'domain/index.html', {'domains': user_domains})

# pylint: disable=too-many-ancestors
class DomainNewView(BaseWizardView):
    """Wizard to create a Domain"""

    title = _("New Domain")
    form_list = [DomainForm]
    registrars = None

    def get_form(self, step=None, data=None, files=None):
        form = super(DomainNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            providers = get_providers(filter_sub=['domain_provider'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                userproductrelationship__user__in=[self.request.user])
            form.fields['provider'].queryset = provider_instance
            form.request = self.request
        return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        domain = form_dict['0'].save(commit=False)
        domain.name = domain.domain
        domain.save()
        UserProductRelationship.objects.create(
            product=domain,
            user=self.request.user)
        messages.success(self.request, _('Domain successfully created'))
        return redirect(reverse('domain-index'))

@login_required
# pylint: disable=unused-argument
def edit(request, domain):
    """Show view to edit account"""
    domains = Domain.objects.filter(domain=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    # Create list of all possible provider instances
    providers = get_providers(filter_sub=['domain_provider'], path=True)
    provider_instance = ProviderInstance.objects.filter(
        provider_path__in=providers,
        userproductrelationship__user__in=[request.user])

    if request.method == 'POST':
        form = DomainForm(request.POST, instance=r_domain)
        form.fields['provider'].queryset = provider_instance
        form.request = request
        if form.is_valid():
            r_domain.save()
            messages.success(request, _('Successfully edited Domain'))
            return redirect(reverse('domain-index'))
    else:
        form = DomainForm(instance=r_domain)
        form.fields['provider'].queryset = provider_instance
        form.request = request
    return render(request, 'core/generic_form_modal.html', {
        'title': "Edit Domain '%s'" % domain,
        'primary_action': 'Save',
        'form': form
        })

@login_required
# pylint: disable=unused-argument
def delete(request, domain):
    """Show view to delete account"""
    domains = Domain.objects.filter(domain=domain)
    if not domains.exists():
        raise Http404
    r_domain = domains.first()

    if request.method == 'POST' and 'confirmdelete' in request.POST:
        # User confirmed deletion
        r_domain.delete()
        messages.success(request, _('Domain successfully deleted'))
        return redirect(reverse('domain-index'))

    return render(request, 'core/generic_delete.html', {
        'object': r_domain.name,
        'delete_url': reverse('domain-delete', kwargs={
            'domain': r_domain.domain,
            })
        })
