"""
Supervisr Core Provider Views
"""

import importlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.provider import NewCredentialForm, NewProviderForm
from supervisr.core.models import BaseCredential
from supervisr.core.providers.base import (BaseProvider, BaseProviderInstance,
                                           ProviderInterfaceAction,
                                           SetupProvider)
from supervisr.core.views.wizard import BaseWizardView


@login_required
def index(req):
    """
    Show a n overview over all provider instances
    """
    user_providers = BaseProviderInstance.objects.filter(
        user__in=[req.user])
    return render(req, 'provider/instance-index.html', {'providers': user_providers})

# pylint: disable=too-many-ancestors
class ProviderNewView(BaseWizardView):
    """
    Wizard to create a Domain
    """

    title = _("New Provider")
    form_list = [NewProviderForm]
    registrars = None
    provider = None
    provider_setup_ui = None

    def get_form(self, step=None, data=None, files=None):
        form = super(ProviderNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            providers = BaseProvider.walk_providers(BaseProvider)
            form.fields['provider'].choices = \
                [('%s.%s' % (s.__module__, s.__name__), s.__name__) for s in providers]
        return form

    def dispatch(self, req, *args, **kwargs):
        print(req.session)
        return super(ProviderNewView, self).dispatch(req, *args, **kwargs)

    def process_step(self, form):
        """
        Dynamically add forms from provider's setup_ui
        """
        if form.__class__ == NewProviderForm:
            # Import provider based on form
            # also check in form if class exists and is subclass of BaseProvider
            parts = form.cleaned_data.get('provider').split('.')
            package = '.'.join(parts[:-1])
            module = importlib.import_module(package)
            _class = getattr(module, parts[-1])
            if _class.setup_ui:
                # create new provider instance
                provider_inst = SetupProvider()
                self.provider_setup_ui = _class.setup_ui(
                    provider_inst, ProviderInterfaceAction.setup, self.request)
                # Add forms to our list
                for idx, _form in enumerate(self.provider_setup_ui.forms):
                    next_idx = str(idx + int(self.steps.current) + 1)
                    # self.form_list is turned into an ordered_dict
                    # pylint: disable=no-member
                    self.form_list.update({next_idx: _form})
        return self.get_form_step_data(form)

    def get_form_initial(self, step):
        if step == '0':
            return self.initial_dict.get(step, {})
        else:
            self.provider_setup_ui.get_form_initial(step)

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        # m_dom = Domain.objects.create(
        #     name=form_dict['0'].cleaned_data.get('domain'),
        #     registrar=form_dict['0'].cleaned_data.get('registrar'),
        #     description='Domain %s' % form_dict['0'].cleaned_data.get('domain'),
        #     )
        # UserProductRelationship.objects.create(
        #     product=m_dom,
        #     user=self.request.user
        #     )
        messages.success(self.request, _('Provider Instance successfully created'))
        return redirect(reverse('provider-instance-index'))

@login_required
def credential_index(req):
    """
    Return a list of all credentials this user has
    """
    creds = BaseCredential.objects.filter(owner=req.user)
    return render(req, 'provider/credentials-index.html', {
        'creds': creds
        })

# pylint: disable=too-many-ancestors
class CredentialNewView(BaseWizardView):
    """
    Wizard to create a Domain
    """

    title = _("New Credentials")
    form_list = [NewCredentialForm]
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
        """
        Dynamically add forms from provider's setup_ui
        """
        if form.__class__ == NewCredentialForm:
            # Import provider based on form
            # also check in form if class exists and is subclass of BaseProvider
            parts = form.cleaned_data.get('credential_type').split('.')
            package = '.'.join(parts[:-1])
            module = importlib.import_module(package)
            _class = getattr(module, parts[-1])
            # pylint: disable=no-member
            self.form_list.update({str(int(self.steps.current) + 1): _class})
        return self.get_form_step_data(form)

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        cred = form_dict['1'].save(commit=False)
        cred.owner = self.request.user
        cred.save()
        messages.success(self.request, _('Credentials successfully created'))
        return redirect(reverse('credential-index'))

@login_required
def credential_delete(req, name):
    """
    Delete Credential
    """
    creds = BaseCredential.objects.filter(name=name, owner=req.user)
    if not creds.exists():
        raise Http404
    r_cred = creds.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_cred.delete()
        messages.success(req, _('Credential successfully deleted'))
        return redirect(reverse('credential-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Credential %s' % r_cred.name,
        'delete_url': reverse('credential-delete', kwargs={
            'name': r_cred.name,
            })
        })
