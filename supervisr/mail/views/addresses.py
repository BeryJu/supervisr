"""supervisr mail address views"""

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.models import ProviderInstance, UserAcquirableRelationship
from supervisr.core.providers.base import get_providers
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericReadView, GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView
from supervisr.mail.forms.addresses import AddressForm
from supervisr.mail.models import Address, MailDomain


class AddressIndexView(GenericIndexView):
    """List of all Addresses"""

    model = Address
    template = 'mail/index.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user]).order_by('mail_address')


# pylint: disable=too-many-ancestors
class AddressNewWizard(BaseWizardView):
    """Wizard to create Address"""

    title = _('New Mail address')
    form_list = [AddressForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(AddressNewWizard, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            domains = MailDomain.objects.filter(users__in=[self.request.user])

            providers = get_providers(capabilities=['mail'], path=True)
            provider_instance = ProviderInstance.objects.filter(
                provider_path__in=providers,
                useracquirablerelationship__user__in=[self.request.user])

            form.fields['domains'].queryset = domains
            form.fields['providers'].queryset = provider_instance
        return form

    def finish(self, form_list):
        mail_address = form_list[0].save(commit=False)
        mail_address.save()
        mail_address.update_provider_m2m(form_list[0].cleaned_data.get('providers'))
        UserAcquirableRelationship.objects.create(
            model=mail_address,
            user=self.request.user)
        messages.success(self.request, _('Mail address successfully created'))
        return redirect(reverse('supervisr_mail:index'))


class AddressReadView(GenericReadView):
    """View details of a single address"""

    model = Address
    template = 'mail/address/view.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         mail_address=self.kwargs.get('address'),
                                         pk=self.kwargs.get('pk'))


class AddressUpdateView(GenericUpdateView):
    """View to edit a single address"""

    model = Address
    form = AddressForm

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         mail_address=self.kwargs.get('address'),
                                         pk=self.kwargs.get('pk'))

    def redirect(self, instance: Address) -> HttpResponse:
        return redirect(reverse('supervisr_mail:index'))


class AddressDeleteView(GenericDeleteView):
    """View to delete a single address"""

    model = Address

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user],
                                         mail_address=self.kwargs.get('address'),
                                         pk=self.kwargs.get('pk'))

    def redirect(self, instance: Address) -> HttpResponse:
        return redirect(reverse('supervisr_mail:index'))
