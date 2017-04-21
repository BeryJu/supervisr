"""
Supervisr Core Domain Views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ..forms.domain import NewDomainForm
from ..models import Domain, UserProductRelationship
from .wizard import BaseWizardView


@login_required
def index(req):
    """
    Show a n overview over all domains
    """
    user_domains = Domain.objects.filter(
        users__in=[req.user])
    return render(req, 'domain/index.html', {'domains': user_domains})

# pylint: disable=too-many-ancestors
class DomainNewView(BaseWizardView):
    """
    Wizard to create a Domain
    """

    title = _("New Domain")
    form_list = [NewDomainForm]
    registrars = None

    # def handle_request(self, request):
    #    Handle loading of registrars here
    #    if self.domains is None:
    #        self.domains = Domain.objects.filter(
    #            users__in=[request.user], maildomain__isnull=True)
    #    if not self.domains:
    #        messages.error(request, _('No Domains available'))
    #        return redirect(reverse('mail:mail-domains'))

    # def get_form(self, step=None, data=None, files=None):
    #     form = super(DomainNewView, self).get_form(step, data, files)
    #     if step is None:
    #         step = self.steps.current
    #     if step == '0':
    #         form.fields['domain'].queryset = self.domains
    #     return form

    # pylint: disable=unused-argument
    def done(self, final_forms, form_dict, **kwargs):
        m_dom = Domain.objects.create(
            name=form_dict['0'].cleaned_data.get('domain'),
            registrar=form_dict['0'].cleaned_data.get('registrar'),
            description='Domain %s' % form_dict['0'].cleaned_data.get('domain'),
            )
        UserProductRelationship.objects.create(
            product=m_dom,
            user=self.request.user
            )
        messages.success(self.request, _('Domain successfully created'))
        return redirect(reverse('domain-index'))
