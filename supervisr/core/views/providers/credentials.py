"""Supervisr Core Provider Views"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.providers import CredentialForm
from supervisr.core.models import BaseCredential
from supervisr.core.utils import path_to_class
from supervisr.core.views.generic import (GenericDeleteView, GenericIndexView,
                                          GenericUpdateView,
                                          LoginRequiredMixin)
from supervisr.core.views.wizards import BaseWizardView


class CredentialIndexView(GenericIndexView):
    """View to index all Credentials"""

    model = BaseCredential
    template = 'provider/credentials-index.html'

    def get_instance(self) -> HttpResponse:
        return self.model.objects.filter(owner=self.request.user).order_by('name')


# pylint: disable=too-many-ancestors
class CredentialNewView(LoginRequiredMixin, BaseWizardView):
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
            if issubclass(_form_class, ModelForm):
                # pylint: disable=no-member
                self.form_list.update({str(int(self.steps.current) + 1): _form_class})
        return self.get_form_step_data(form)

    def finish(self, *forms):
        if len(forms) < 2:
            raise ValidationError(_('No type selected'))
        cred = forms[1].save(commit=False)
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
