"""
Supervisr Core Provider Views
"""

import importlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ..forms.provider import NewProviderForm
from ..providers.base import (BaseProvider, BaseProviderInstance,
                              ProviderInterfaceAction, SetupProvider)
from .wizard import BaseWizardView


@login_required
def index(req):
    """
    Show a n overview over all provider instances
    """
    user_providers = BaseProviderInstance.objects.filter(
        user__in=[req.user])
    return render(req, 'provider/provider-index.html', {'providers': user_providers})

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

    def process_step(self, form):
        """
        Dynamically add forms from provider's setup_ui
        """
        print(len(self.form_list))
        if form.__class__ == NewProviderForm:
            # Import provider based on form
            # TODO: also check in form if class exists and is subclass of BaseProvider
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
        return redirect(reverse('provider-index'))
