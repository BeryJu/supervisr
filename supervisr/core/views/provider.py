"""
Supervisr Core Provider Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ..forms.provider import NewProviderForm
from ..providers.base import BaseProvider, BaseProviderInstance
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

    def get_form(self, step=None, data=None, files=None):
        form = super(ProviderNewView, self).get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '0':
            # pylint: disable=no-member
            subclasses = BaseProvider.__subclasses__()
            form.fields['provider'].choices = [(s.__qualname__, s.ui_name) for s in subclasses]
        return form

    def get_form_initial(self, step):
        if step == 0:
            return self.initial_dict.get(step, {})
        else:
            self.provider.interface_ui.get_form_initial(step)

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
