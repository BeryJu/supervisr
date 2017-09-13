"""
Supervisr Core Provider Views
"""

import importlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.providers import CredentialForm, ProviderForm
from supervisr.core.models import (BaseCredential, ProviderInstance,
                                   UserProductRelationship)
from supervisr.core.providers.base import get_providers
from supervisr.core.views.wizards import BaseWizardView


@login_required
def instance_index(req):
    """
    Show a n overview over all provider instances
    """
    user_providers = ProviderInstance.objects.filter(users__in=[req.user])
    return render(req, 'provider/instance-index.html', {'providers': user_providers})

PROVIDER_TEMPLATES = {
    '0': 'provider/instance-wizard.html',
    '1': 'core/generic_wizard.html',
}

# pylint: disable=too-many-ancestors
class ProviderNewView(BaseWizardView):
    """
    Wizard to create a Domain
    """

    title = _("New Provider")
    providers = None
    form_list = [ProviderForm]

    def get_form(self, step=None, data=None, files=None):
        form = super(ProviderNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            self.providers = get_providers()
            creds = BaseCredential.objects.filter(owner=self.request.user)
            form.fields['provider_path'].choices = \
                [('%s.%s' % (s.__module__, s.__class__.__name__), s.get_meta.ui_name)
                 for s in self.providers]
            form.fields['credentials'].queryset = creds
            form.request = self.request
        return form

    def get_context_data(self, form, **kwargs):
        context = super(ProviderNewView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '0':
            context.update({'providers': self.providers})
        return context

    def get_template_names(self):
        return [PROVIDER_TEMPLATES[self.steps.current]]

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        creds = form_dict['0'].cleaned_data.get('credentials')
        if not creds.owner == self.request.user:
            raise Http404

        r_creds = creds.cast()

        prov_inst = ProviderInstance.objects.create(
            name=form_dict['0'].cleaned_data.get('name'),
            credentials=r_creds,
            provider_path=form_dict['0'].cleaned_data.get('provider_path'))

        UserProductRelationship.objects.create(
            product=prov_inst,
            user=self.request.user)
        messages.success(self.request, _('Provider Instance successfully created'))
        return redirect(reverse('instance-index'))

@login_required
def instance_edit(req, uuid):
    """
    Edit Instance
    """
    inst = ProviderInstance.objects.filter(uuid=uuid, users__in=[req.user])
    if not inst.exists():
        raise Http404
    r_inst = inst.first()

    providers = get_providers()
    creds = BaseCredential.objects.filter(owner=req.user)
    form_providers = [('%s.%s' % (s.__module__, s.__class__.__name__),
                       '%s (%s)' % (s.get_meta.ui_name, s.__class__.__name__)) for s in providers]

    if req.method == 'POST':
        form = ProviderForm(req.POST, instance=r_inst)
        form.request = req
        form.fields['provider_path'].choices = form_providers
        form.fields['credentials'].queryset = creds

        if form.is_valid():
            form.save()
            messages.success(req, _('Successfully edited Instance'))
            return redirect(reverse('instance-index'))
        messages.error(req, _('Invalid Instance'))
    else:
        form = ProviderForm(instance=r_inst)
        form.request = req
        form.fields['provider_path'].choices = form_providers
        form.fields['credentials'].queryset = creds

    return render(req, 'core/generic_form_modal.html', {
        'form': form,
        'title': 'Edit %s' % r_inst.name,
        })

@login_required
def instance_delete(req, uuid):
    """
    Delete Instance
    """
    inst = ProviderInstance.objects.filter(uuid=uuid,
                                           userproductrelationship__user__in=[req.user])
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
        'title': 'Delete %s' % r_inst.name,
        'delete_url': reverse('instance-delete', kwargs={
            'uuid': r_inst.uuid,
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
        """
        Dynamically add forms from provider's setup_ui
        """
        if form.__class__ == CredentialForm:
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
        if '1' not in form_dict:
            raise ValidationError(_('No type selected'))
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
        'title': 'Delete %s' % r_cred.name,
        'delete_url': reverse('credential-delete', kwargs={
            'name': r_cred.name,
            })
        })