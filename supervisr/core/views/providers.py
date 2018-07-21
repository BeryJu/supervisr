"""Supervisr Core Provider Views"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from supervisr.core.forms.providers import CredentialForm, ProviderForm
from supervisr.core.models import (BaseCredential, ProviderInstance,
                                   UserAcquirableRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.utils import class_to_path, path_to_class
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView)
from supervisr.core.views.wizards import BaseWizardView


class ProviderIndexView(GenericIndexView):
    """Show an overview over all provider instances"""

    model = ProviderInstance
    template = 'provider/instance-index.html'

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(users__in=[self.request.user]).order_by('name')


PROVIDER_TEMPLATES = {
    '0': 'provider/instance-wizard.html',
    '1': 'core/generic_wizard.html',
}


# pylint: disable=too-many-ancestors
class ProviderCreateView(BaseWizardView):
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

    def finish(self, form_list):
        credentials = form_list[0].cleaned_data.get('credentials')
        if not credentials.owner == self.request.user:
            raise Http404

        r_credentials = credentials.cast()

        prov_inst = ProviderInstance.objects.create(
            name=form_list[0].cleaned_data.get('name'),
            credentials=r_credentials,
            provider_path=form_list[0].cleaned_data.get('provider_path'))

        UserAcquirableRelationship.objects.create(
            model=prov_inst,
            user=self.request.user)
        messages.success(self.request, _('Provider Instance successfully created'))
        return redirect(reverse('instance-index'))


class ProviderUpdateView(GenericUpdateView):
    """Update instance"""

    model = ProviderInstance
    form = ProviderForm

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(uuid=self.kwargs.get('uuid'),
                                         users__in=[self.request.user])

    def update_form(self, form: ProviderForm) -> ProviderForm:
        providers = get_providers()
        credentials = BaseCredential.objects.filter(owner=self.request.user)
        form_providers = [(class_to_path(s),
                           '%s (%s)' % (s.Meta(None).ui_name, s.__class__.__name__))
                          for s in providers]

        form.request = self.request
        form.fields['provider_path'].choices = form_providers
        form.fields['credentials'].queryset = credentials
        return form

    def redirect(self, instance: ProviderInstance) -> HttpResponse:
        return redirect(reverse('instance-index'))


class ProviderDeleteView(GenericDeleteView):
    """Delete instance"""

    model = ProviderInstance

    def get_instance(self) -> QuerySet:
        return self.model.objects.filter(uuid=self.kwargs.get('uuid'),
                                         useracquirablerelationship__user__in=[self.request.user])

    def redirect(self, instance: ProviderInstance) -> HttpResponse:
        return redirect(reverse('instance-index'))


class CredentialIndexView(GenericIndexView):
    """View to index all Credentials"""

    model = BaseCredential
    template = 'provider/credentials-index.html'

    def get_instance(self) -> HttpResponse:
        return self.model.objects.filter(owner=self.request.user).order_by('name')


# pylint: disable=too-many-ancestors
class CredentialNewView(BaseWizardView):
    """Wizard to create a Domain"""

    title = _("New Credentials")
    form_list = [CredentialForm]
    registrars = None
    provider = None
    provider_setup_ui = None

    def get_form(self, step=None, data=None, files=None):
        form = super(CredentialNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            cred_types = BaseCredential.all_types()
            form.fields['credential_type'].choices = \
                [(c.form, c.type()) for c in cred_types]
        return form

    def process_step(self, form):
        """Dynamically add forms from provider's setup_ui"""
        if form.__class__ == CredentialForm:
            # Import provider based on form
            # also check in form if class exists and is subclass of BaseProvider
            _form_class = path_to_class(form.cleaned_data.get('credential_type'))
            assert issubclass(_form_class, ModelForm)
            # pylint: disable=no-member
            self.form_list.update({str(int(self.steps.current) + 1): _form_class})
        return self.get_form_step_data(form)

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        if '1' not in form_dict:
            raise ValidationError(_('No type selected'))
        cred = form_dict['1'].save(commit=False)
        cred.owner = self.request.user
        cred.save()
        messages.success(self.request, _('Credentials successfully created'))
        return redirect(reverse('credential-index'))


class CredentialUpdateView(GenericUpdateView):
    """Update Credential"""

    model = BaseCredential
    form = ModelForm

    def get_instance(self) -> QuerySet:
        query_set = self.model.objects.filter(name=self.kwargs.get('name'),
                                              owner=self.request.user)
        # Get form class from credential instance
        self.form = path_to_class(query_set.first().cast().form)
        return query_set

    def redirect(self, instance: BaseCredential) -> HttpResponse:
        return redirect(reverse('credential-index'))


class CredentialDeleteView(GenericDeleteView):
    """View to delete Credential"""

    model = BaseCredential

    def redirect(self, instance: BaseCredential) -> HttpResponse:
        return redirect(reverse('credential-index'))

    def get_instance(self) -> QuerySet:
        """Get domain from name"""
        return self.model.objects.filter(name=self.kwargs.get('name'),
                                         owner=self.request.user)
