"""supervisr mail domain views"""

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import (Domain, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericReadView, GenericUpdateView,
                                          LoginRequiredMixin)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.domains import MailDomainForm
from supervisr.mail.models import MailDomain


class MailDomainIndexView(GenericIndexView):
    """List of all MailDomains"""

    model = MailDomain
    template = 'mail/index.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user]) \
                                 .order_by('domain__domain_name')


# pylint: disable=too-many-ancestors
class MailDomainNewWizard(LoginRequiredMixin, BaseWizardView):
    """Wizard to create MailDomain"""

    title = _('New Mail Domain')
    form_list = [MailDomainForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(MailDomainNewWizard, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            domains = MailDomain.objects.filter(users__in=[self.request.user])

            unused_domains = Domain.objects.filter(users__in=[self.request.user]) \
                .exclude(pk__in=domains.values_list('domain', flat=True))

            providers = get_providers(capabilities=['mail'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])

            form.fields['domain'].queryset = unused_domains
            form.fields['providers'].queryset = provider_instance
        return form

    def finish(self, form):
        mail_domain = form.save(commit=False)
        mail_domain.save()
        mail_domain.update_provider_m2m(form.cleaned_data.get('providers'))
        UserAcquirableRelationship.objects.create(
            model=mail_domain,
            user=self.request.user)
        messages.success(self.request, _('Mail Domain successfully created'))
        return redirect(reverse('supervisr_mail:index'))


class MailDomainReadView(GenericReadView):
    """View details of a single domain"""

    model = MailDomain
    template = 'mail/domains/view.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         domain__domain_name=self.kwargs.get('domain'))


class MailDomainUpdateView(GenericUpdateView):
    """View to edit a single domain"""

    model = MailDomain
    form = MailDomainForm

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         domain__domain_name=self.kwargs.get('domain'))

    def redirect(self, instance: MailDomain) -> HttpResponse:
        return redirect(reverse('supervisr_mail:index'))


class MailDomainDeleteView(GenericDeleteView):
    """View to delete a single domain"""

    model = MailDomain

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         domain__domain_name=self.kwargs.get('domain'))

    def redirect(self, instance: MailDomain) -> HttpResponse:
        return redirect(reverse('supervisr_mail:index'))
