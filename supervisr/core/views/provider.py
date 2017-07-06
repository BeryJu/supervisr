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
from supervisr.core.models import BaseCredential, UserProductRelationship
from supervisr.core.providers.base import BaseProvider, BaseProviderInstance
from supervisr.core.views.wizard import BaseWizardView


@login_required
def instance_index(req):
    """
    Show a n overview over all provider instances
    """
    user_providers = BaseProviderInstance.objects.filter(
        userproductrelationship__user__in=[req.user])
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
            creds = BaseCredential.objects.filter(owner=self.request.user)
            form.fields['provider'].choices = \
                [('%s.%s' % (s.__module__, s.__name__), s.ui_name) for s in providers]
            form.fields['credentials'].choices = \
                [(c.name, '%s: %s' % (c.cast().type(), c.name)) for c in creds]
            form.request = self.request
        return form

    def get_form_initial(self, step):
        if step == '0':
            return self.initial_dict.get(step, {})
        else:
            self.provider_setup_ui.get_form_initial(step)

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        creds = BaseCredential.objects.filter(name=form_dict['0'].cleaned_data.get('credentials'),
                                              owner=self.request.user)
        if not creds.exists():
            raise Http404
        r_creds = creds.first().cast()

        prov_inst = BaseProviderInstance.objects.create(
            name=form_dict['0'].cleaned_data.get('name'),
            credentials=r_creds,
            provider_path=form_dict['0'].cleaned_data.get('provider'))

        UserProductRelationship.objects.create(
            product=prov_inst,
            user=self.request.user)
        messages.success(self.request, _('Provider Instance successfully created'))
        return redirect(reverse('instance-index'))

@login_required
# pylint: disable=invalid-name
def instance_delete(req, pk):
    """
    Delete Instance
    """
    inst = BaseProviderInstance.objects.filter(pk=pk, userproductrelationship__user__in=[req.user])
    if not inst.exists():
        raise Http404
    r_inst = inst.first()

    if req.method == 'POST' and 'confirmdelete' in req.POST:
        # User confirmed deletion
        r_inst.delete()
        messages.success(req, _('Instance successfully deleted'))
        return redirect(reverse('instance-index'))

    return render(req, 'core/generic_delete.html', {
        'object': 'Instance %s' % r_inst.name,
        'delete_url': reverse('instance-delete', kwargs={
            'pk': r_inst.pk,
            })
        })

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
