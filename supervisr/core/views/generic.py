"""Generic, reusable Class-based views"""
import warnings
from typing import Union

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.query import Q, QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View

from supervisr.core.decorators import anonymous_required
from supervisr.core.models import CastableModel, UserAcquirable


class LoginRequiredMixin(View):
    """Utility View class that always requires login"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AnonymousRequiredMixin(View):
    """Utility View class that always requires user to not be authenticated"""

    @method_decorator(anonymous_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AdminRequiredMixin(View):
    """Utility View class that requires superuser"""

    @method_decorator(user_passes_test(lambda user: user.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class GenericModelView(LoginRequiredMixin):
    """Generic View to interact with a model"""

    model = None
    model_verbose_name = ''
    template = None
    template_name = None
    redirect_view = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.template is not None:
            warnings.warn("self.template is deprecated in favor of self.template_name",
                          DeprecationWarning)
            self.template_name = self.template
        if self.template_name is None:
            raise ValueError("`template_name` Property has to be overwritten")
        if self.model is None:
            raise ValueError("`model` Property has to be overwritten")
        if self.model_verbose_name == '':
            self.model_verbose_name = self.model._meta.verbose_name.title()

    def get_instance(self) -> QuerySet:
        """Get model instance. Here you can apply extra filters.

        By default we filter with the argument `pk` matching `pk`.
        Default sorting is done by `pk`.
        This method should return a QuerySet."""
        query = Q()
        if 'pk' in self.kwargs:
            query &= Q(pk=self.kwargs.get('pk'))
        if 'uuid' in self.kwargs:
            query &= Q(uuid=self.kwargs.get('uuid'))
        if issubclass(self.model, UserAcquirable):
            query &= Q(users__in=[self.request.user])

        if query:
            return self.model.objects.filter(query).order_by('pk')
        raise NotImplementedError()

    def _redirect_helper(self, *args, **kwargs) -> HttpResponse:
        """self.redirect may return a string. In this case, reverse
        string into a HttpRedirectResponse."""
        if 'back' in self.request.GET:
            return redirect(self.request.GET.get('back'))
        if self.redirect_view is not None:
            return redirect(reverse(self.redirect_view))
        response = self.redirect(*args, **kwargs)
        if isinstance(response, str):
            return redirect(reverse(response))
        return response

    # pylint: disable=unused-argument
    def redirect(self, instance) -> Union[HttpResponse, str]:
        """Redirect after a successful write operation"""
        return ''


class GenericIndexView(GenericModelView):
    """Generic view to view a list of objects"""

    def render(self, kwargs: dict) -> HttpResponse:
        """Render template with kwargs"""
        return render(self.request, self.template_name, kwargs)

    def update_kwargs(self, kwargs: dict) -> dict:
        """Add additional data to render kwargs"""
        return kwargs

    def redirect(self, instance) -> Union[HttpResponse, str]:
        """This method isn't used by GenericIndexView"""
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

    def redirect(self, instance) -> Union[HttpResponse, str]:
        """Since this a read-only view we don't need this method"""
        pass

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle get request"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        render_kwargs = self.update_kwargs({'instance': instance})
        return self.render(render_kwargs)


class GenericUpdateView(GenericModelView):
    """Generic view to edit an object instance"""

    form = None
    template_name = 'generic/form_modal.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.form is None:
            raise ValueError("`form` Property has to be overwritten")
        if not issubclass(self.form, ModelForm):
            raise ValueError("`form` Property should be a ModelForm")

    def render(self, form) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template_name, {
            'form': form,
            'primary_action': 'Save',
            'title': 'Edit %s' % self.model_verbose_name,
        })

    def get_form(self, *args, instance: models.Model, **kwargs) -> ModelForm:
        """Get form instance. *args and **kwargs should be passed to Form Constructor."""
        # pylint: disable=not-callable
        form_instance = self.form(*args, instance=instance, **kwargs)
        if getattr(self, 'update_form', False):
            warnings.warn('GenericUpdateView.update_form is deprecated in favor of get_form.')
            return getattr(self, 'update_form')(form_instance)
        return form_instance

    def save(self, form: ModelForm) -> models.Model:
        """Save the data from the form"""
        return form.save()

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Get request"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        form = self.get_form(instance=instance)
        return self.render(form)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Post request"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        form = self.get_form(request.POST, instance=instance)
        if form.is_valid():
            self.save(form)
            messages.success(self.request, _('Successfully edited %(verbose_name)s'
                                             % {'verbose_name': self.model_verbose_name}))
            return self._redirect_helper(instance)
        return self.render(form)


class GenericDeleteView(GenericModelView):
    """Generic View to delete model instances"""

    template_name = 'generic/delete.html'

    def render(self, instance) -> HttpResponse:
        """Render the template and return a HttpResponse"""
        return render(self.request, self.template_name, {
            'verbose_name': self.model_verbose_name,
            'instance_name': instance.name if getattr(instance, 'name', None) else str(instance)
        })

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Get request"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        return self.render(instance)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Handle Post request"""
        instance = get_object_or_404(self.get_instance())
        if isinstance(instance, CastableModel):
            instance = instance.cast()
        if 'confirmdelete' in request.POST:
            instance.delete()
            messages.success(self.request, _('Successfully deleted %(verbose_name)s'
                                             % {'verbose_name': self.model_verbose_name}))
            return self._redirect_helper(instance)
        return self.render(instance)
