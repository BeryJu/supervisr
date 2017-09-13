"""
Supervisr Core Base Wizard Views
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from formtools.wizard.views import SessionWizardView


# pylint: disable=too-many-ancestors
class BaseWizardView(SessionWizardView):
    """
    Base Wizard view, sets a template and adds a title
    """

    template_name = 'core/generic_wizard.html'
    _handle_request_res = None
    _referer = ''
    _request = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BaseWizardView, self).dispatch(*args, **kwargs)

    def handle_request(self, req):
        """
        Do things with data from req and save to self
        """
        self._request = req
        # Check if this is the first call
        if not any(f.endswith('-current_step') for f in req.POST):
            # Save referal if there is one
            if 'HTTP_REFERER' in req.META:
                self._referer = req.META.get('HTTP_REFERER')
                req.session['%s_referer' % self.__class__.__name__] = self._referer
        if '%s_referer' % self.__class__.__name__ in req.session:
            self._referer = req.session.get('%s_referer' % self.__class__.__name__)

    def get(self, req, *args, **kwargs):
        self._handle_request_res = self.handle_request(req)
        return super(BaseWizardView, self).get(req, *args, **kwargs)

    def post(self, req, *args, **kwargs):
        self._handle_request_res = self.handle_request(req)
        return super(BaseWizardView, self).post(req, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(BaseWizardView, self).get_context_data(form=form, **kwargs)
        context['title'] = self.title
        context['back'] = self._referer
        return context

    def render(self, form=None, **kwargs):
        if isinstance(self._handle_request_res, HttpResponse):
            return self._handle_request_res
        return super(BaseWizardView, self).render(form, **kwargs)

    def done(self, form_list, **kwargs):
        # Cleanup session
        if '%s_referer' % self.__class__.__name__ in self._request.session:
            del self._request.session['%s_referer' % self.__class__.__name__]
