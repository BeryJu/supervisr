"""Generic, reusable Class-based views"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View


class GenericModelView(View):
    """Generic View to interact with a model"""

    model = None
    model_verbose_name = ''
    template = None

    def __init__(self, *args, **kwargs):
        super(GenericModelView, self).__init__(*args, **kwargs)
        assert self.model is not None, "`model` Property has to be overwritten"
        if self.model_verbose_name == '':
            self.model_verbose_name = self.model._meta.verbose_name.title()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GenericModelView, self).dispatch(*args, **kwargs)

    def get_instance(self) -> QuerySet:
        """Get model instance. Here you can apply extra filters.

        By default we filter with the argument `pk` matching `pk`.
        This method should return a QuerySet.
        """
        if 'pk' in self.kwargs:
            return self.model.filter(pk=self.kwargs.get('pk'))
        raise NotImplementedError()

    def redirect(self, instance) -> HttpResponse:
        """Redirect after a successful edit"""
        raise NotImplementedError()

# pylint: disable=abstract-method
class GenericEditView(GenericModelView):
    """Generic view to edit an object instance"""

    form = None
    template = 'core/generic_form_modal.html'

    def __init__(self, *args, **kwargs):
        super(GenericEditView, self).__init__(*args, **kwargs)
        assert self.form is not None, "`form` Property has to be overwritten"
        assert issubclass(self.form, ModelForm), "`form` Property should be a ModelForm"

    def render(self, form) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template, {
            'form': form,
            'primary_action': 'Save',
            'title': 'Edit %s' % self.model_verbose_name,
            })

    def update_form(self, form) -> ModelForm:
        """Edit form instance after it has been instantiated"""
        return form

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Get request"""
        instances = self.get_instance()
        if not instances.exists():
            raise Http404
        assert len(instances) == 1, "More than 1 Result found."
        instance = instances.first()
        # pylint: disable=not-callable
        form = self.update_form(self.form(instance=instance))
        return self.render(form)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Post request"""
        instances = self.get_instance()
        if not instances.exists():
            raise Http404
        assert len(instances) == 1, "More than 1 Result found."
        instance = instances.first()
        # pylint: disable=not-callable
        form = self.update_form(self.form(request.POST, instance=instance))
        if form.is_valid():
            form.save()
            messages.success(self.request, _('Successfully edited %(verbose_name)s'
                                             % self.model_verbose_name))
            return self.redirect(instance)
        return self.render(form)

# pylint: disable=abstract-method
class GenericDeleteView(GenericModelView):
    """Generic View to delete model instances"""

    template = 'core/generic_delete.html'

    def render(self, instance) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template, {
            'verbose_name': self.model_verbose_name,
            'instance_name': instance.name if getattr(instance, 'name', None) else str(instance)
            })

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Get request"""
        instances = self.get_instance()
        if not instances.exists():
            raise Http404
        assert len(instances) == 1, "More than 1 Result found."
        instance = instances.first()
        return self.render(instance)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Post request"""
        instances = self.get_instance()
        if not instances.exists():
            raise Http404
        assert len(instances) == 1, "More than 1 Result found."
        instance = instances.first()
        # pylint: disable=not-callable
        if 'confirmdelete' in request.POST:
            instance.delete()
            messages.success(self.request, _('Successfully deleted %(verbose_name)s'
                                             % {'verbose_name': self.model_verbose_name}))
            return self.redirect(instance)
        return self.render(instance)
