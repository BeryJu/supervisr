"""Supervisr Core Provider Views"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.providers import ProviderForm
from supervisr.core.models import (BaseCredential, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.utils import class_to_path
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView,
                                          LoginRequiredMixin)
from supervisr.core.views.wizards import BaseWizardView


class ProviderIndexView(GenericIndexView):
    """Show an overview over all provider instances"""

    model = ProviderInstance
    template = 'provider/instance-index.html'


PROVIDER_TEMPLATES = {
    '0': 'provider/instance-wizard.html',
    '1': 'generic/wizard.html',
}


# pylint: disable=too-many-ancestors
class ProviderCreateView(LoginRequiredMixin, BaseWizardView):
    """Wizard to create a Domain"""

    title = _("New Provider")
    providers = None
    form_list = [ProviderForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(ProviderCreateView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            self.providers = get_providers()
            creds = BaseCredential.objects.filter(owner=self.request.user)
            form.fields['provider_path'].choices = [(class_to_path(s), s.Meta(None).ui_name)
                                                    for s in self.providers]
            form.fields['credentials'].queryset = creds
            form.request = self.request
        return form

    def get_context_data(self, form, **kwargs):
        context = super(ProviderCreateView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '0':
            template_provider_info = {}
            for provider in self.providers:
                provider_meta = provider.Meta(None)
                template_provider_info[class_to_path(provider)] = {
                    'ui_name': provider_meta.ui_name,
                    'ui_description': provider_meta.ui_description,
                    'capabilities': ', '.join(provider_meta.capabilities),
                    'author': provider_meta.get_author,
                }
            context.update({'providers': template_provider_info})
        return context

    def get_template_names(self):
        return [PROVIDER_TEMPLATES[self.steps.current]]

    def finish(self, form):
        credentials = form.cleaned_data.get('credentials')
        if not credentials.owner == self.request.user:
            raise Http404

        r_credentials = credentials.cast()

        prov_inst = ProviderInstance.objects.create(
            name=form.cleaned_data.get('name'),
            credentials=r_credentials,
            provider_path=form.cleaned_data.get('provider_path'))

        UserAcquirableRelationship.objects.create(
            model=prov_inst,
            user=self.request.user)
        messages.success(self.request, _('Provider Instance successfully created'))
        return redirect(reverse('instance-index'))


class ProviderUpdateView(GenericUpdateView):
    """Update instance"""

    model = ProviderInstance
    form = ProviderForm
    redirect_view = 'instance-index'

    def get_form(self, *args, instance: ProviderInstance, **kwargs) -> ProviderForm:
        form = super().get_form(*args, instance=instance, **kwargs)
        providers = get_providers()
        credentials = BaseCredential.objects.filter(owner=self.request.user)
        form_providers = [(class_to_path(s),
                           '%s (%s)' % (s.Meta(None).ui_name, s.__class__.__name__))
                          for s in providers]

        form.request = self.request
        form.fields['provider_path'].choices = form_providers
        form.fields['credentials'].queryset = credentials
        return form


class ProviderDeleteView(GenericDeleteView):
    """Delete instance"""

    model = ProviderInstance
    redirect_view = 'instance-index'
