"""
Supervisr Core Base Wizard Views
"""

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView


# pylint: disable=too-many-ancestors
class BaseWizardView(SessionWizardView):
    """
    Base Wizard view, sets a template and adds a title
    """

    template_name = 'core/generic_wizard.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BaseWizardView, self).dispatch(*args, **kwargs)

    def handle_request(self, req):
        """
        Do things with data from req and save to self
        """
        pass

    def get(self, req, *args, **kwargs):
        self.handle_request(req)
        return super(BaseWizardView, self).get(req, *args, **kwargs)

    def post(self, req, *args, **kwargs):
        self.handle_request(req)
        return super(BaseWizardView, self).post(req, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(BaseWizardView, self).get_context_data(form=form, **kwargs)
        context['title'] = self.title
        return context

    def done(self, *args, **kwargs):
        pass
