"""Supervisr Core Base Wizard Views"""
from typing import Union

from django.forms import Form
from django.http import HttpRequest, HttpResponse
from formtools.wizard.views import NamedUrlSessionWizardView, SessionWizardView


# pylint: disable=too-many-ancestors
class BaseWizardView(SessionWizardView):
    """Base Wizard view, sets a template and adds a title"""

    template_name = 'generic/wizard.html'
    wizard_size = 'lg'
    title = ''
    _handle_request_res = None
    _referer = ''
    _request = None

    def handle_request(self, request: HttpRequest) -> Union[HttpResponse, bool]:
        """Do things with data from request and save to self"""
        self._request = request
        # Check if this is the first call
        if not any(f.endswith('-current_step') for f in request.POST):
            # Save referal if there is one
            if 'HTTP_REFERER' in request.META:
                self._referer = request.META.get('HTTP_REFERER')
                request.session['%s_referer' % self.__class__.__name__] = self._referer
        if '%s_referer' % self.__class__.__name__ in request.session:
            self._referer = request.session.get('%s_referer' % self.__class__.__name__)
        return True

    def get(self, request: HttpRequest, *args, **kwargs):
        self._handle_request_res = self.handle_request(request)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        self._handle_request_res = self.handle_request(request)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, form: Form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['title'] = self.title
        context['back'] = self._referer
        context['size'] = self.wizard_size
        return context

    def render(self, form: Form = None, **kwargs):
        if isinstance(self._handle_request_res, HttpResponse):
            return self._handle_request_res
        return super().render(form, **kwargs)

    def finish(self, *forms) -> HttpResponse:
        """Wrapper for done with an actual list as param"""
        raise NotImplementedError()

    def done(self, form_list, **kwargs):
        # Cleanup session
        if '%s_referer' % self.__class__.__name__ in self._request.session:
            del self._request.session['%s_referer' % self.__class__.__name__]
        # convert ordered dict to normal dict,
        # convert int in string to just int
        _form_list = []
        for form in form_list:
            _form_list.append(form)
        return self.finish(*_form_list)


class NamedWizard(BaseWizardView, NamedUrlSessionWizardView):
    """Same as BaseWizardView except with named steps"""

    def finish(self, *forms) -> HttpResponse:
        raise NotImplementedError()
