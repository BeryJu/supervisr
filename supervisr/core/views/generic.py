"""Generic, reusable Class-based views"""
import warnings

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View


class LoginRequiredView(View):
    """Utility View class that always requires login"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)


class AdminRequiredView(View):
    """Utility View class that requires superuser"""

    @method_decorator(user_passes_test(lambda user: user.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(AdminRequiredView, self).dispatch(*args, **kwargs)


class GenericModelView(LoginRequiredView):
    """Generic View to interact with a model"""

    model = None
    model_verbose_name = ''
    template = None
    template_name = None

    def __init__(self, *args, **kwargs):
        super(GenericModelView, self).__init__(*args, **kwargs)
        if self.template is not None:
            warnings.warn("self.template is deprected in favor of self.template_name",
                          DeprecationWarning)
            self.template_name = self.template
        assert self.template_name is not None, "`template_name` Property has to be overwritten"
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
        """Redirect after a successful write operation"""
        raise NotImplementedError()


class GenericIndexView(GenericModelView):
    """Generic view to view a list of objects"""

    def render(self, kwargs: dict) -> HttpResponse:
        """Render template with kwargs"""
        return render(self.request, self.template_name, kwargs)

    def update_kwargs(self, kwargs: dict) -> dict:
        """Add additional data to render kwargs"""
        return kwargs

    def redirect(self, instance) -> HttpResponse:
        """This method isnt used by GenericIndexView"""
        pass

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle get request"""
        instances = self.get_instance()
        paginator = Paginator(instances, request.user.rows_per_page)

        page = request.GET.get('page')
        try:
            page_instances = paginator.page(page)
        except PageNotAnInteger:
            page_instances = paginator.page(1)
        except EmptyPage:
            page_instances = paginator.page(paginator.num_pages)

        render_kwargs = self.update_kwargs({'instances': page_instances})
        return self.render(render_kwargs)


class GenericReadView(GenericModelView):
    """Generic view to view an object instance"""

    def render(self, kwargs) -> HttpResponse:
        """Render template with kwargs"""
        return render(self.request, self.template_name, kwargs)

    def update_kwargs(self, kwargs) -> dict:
        """Add additional data to render kwargs"""
        return kwargs

    def redirect(self, instance) -> HttpResponse:
        """Since this a read-only view we don't need this method"""
        pass

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle get request"""
        instances = self.get_instance()
        if not instances.exists():
            raise Http404
        assert len(instances) == 1, "More than 1 Result found."
        instance = instances.first()
        render_kwargs = self.update_kwargs({'instance': instance})
        return self.render(render_kwargs)


# pylint: disable=abstract-method
class GenericUpdateView(GenericModelView):
    """Generic view to edit an object instance"""

    form = None
    template_name = 'core/generic_form_modal.html'

    def __init__(self, *args, **kwargs):
        super(GenericUpdateView, self).__init__(*args, **kwargs)
        assert self.form is not None, "`form` Property has to be overwritten"
        assert issubclass(
            self.form, ModelForm), "`form` Property should be a ModelForm"

    def render(self, form) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template_name, {
            'form': form,
            'primary_action': 'Save',
            'title': 'Edit %s' % self.model_verbose_name,
        })

    def update_form(self, form) -> ModelForm:
        """Edit form instance after it has been instantiated"""
        return form

    def save(self, form: ModelForm) -> models.Model:
        """Save the data from the form"""
        return form.save()

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
            self.save(form)
            messages.success(self.request, _('Successfully edited %(verbose_name)s'
                                             % {'verbose_name': self.model_verbose_name}))
            return self.redirect(instance)
        return self.render(form)


# pylint: disable=abstract-method
class GenericDeleteView(GenericModelView):
    """Generic View to delete model instances"""

    template_name = 'core/generic_delete.html'

    def render(self, instance) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template_name, {
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
        if 'confirmdelete' in request.POST:
            instance.delete()
            messages.success(self.request, _('Successfully deleted %(verbose_name)s'
                                             % {'verbose_name': self.model_verbose_name}))
            return self.redirect(instance)
        return self.render(instance)
