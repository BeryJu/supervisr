"""
Supervisr Core r1 Model API
"""

from django import forms
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.http import Http404, QueryDict
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from supervisr.core.models import Product, UserProductRelationship
from supervisr.core.views.api.utils import api_response


class ModelAPI(View):
    """
    Basic API for Models
    """

    model = None
    form = None

    queryable_fields = ['name']
    viewable_fields = ['name']
    editable_fields = ['name']

    ALLOWED_VERBS = {
        'GET': ['read'],
        'POST': ['create', 'update', 'delete'],
    }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        my_allowed = self.ALLOWED_VERBS[request.method]
        verb = kwargs['verb']
        if verb not in my_allowed:
            return api_response(request, {'error': 'verb not allowed in HTTP VERB'})

        if request.method in ['PUT', 'DELETE']:
            data = QueryDict(request.body).dict()
        elif request.method == 'POST':
            data = request.POST.dict()
        elif request.method == 'GET':
            data = request.GET.dict()

        self.fields_from_form()

        handler = getattr(self, verb, None)
        if handler:
            try:
                return api_response(request, handler(request, data))
            except Http404:
                return api_response(request, {'error': '404'})
            except KeyError as exc:
                return api_response(request, {'error': exc.args[0]})

    def fields_from_form(self):
        """
        Check if form is set and read fields from it
        """
        if self.form:
            # pylint: disable=not-callable
            form = self.form()
            if isinstance(form, forms.ModelForm):
                fields = self.form.Meta.fields
                self.queryable_fields = fields
                self.viewable_fields = fields
                self.editable_fields = fields
                return True
        return False

    @staticmethod
    def user_filter(queryset, user):
        """
        This method is used to check if the user has access
        """
        if not user.is_authenticated:
            raise Http404
        return queryset.filter(users__in=[user])

    def model_to_dict(self, qs):
        """
        Convert queryset to dict
        """
        final_dict = {}
        for m_inst in qs:
            final_dict[m_inst.pk] = {}
            for field in self.viewable_fields:
                data = getattr(m_inst, field, None)
                if isinstance(data, models.Model):
                    data = data.pk
                final_dict[m_inst.pk][field] = data
        return final_dict

    @staticmethod
    def sanitize_data(data, keyset):
        """
        Sanitize data with keyset
        """
        new_data = {}
        for key, value in data.items():
            if key in keyset:
                new_data[key] = value
        return new_data

    @staticmethod
    def check_keys(data, keyset):
        """
        Check if data has all keys it should have
        """
        for key in keyset:
            if key not in data:
                raise KeyError('Key %s not in data' % key)
        return True

    def fill_with_defaults(self, data):
        """
        Fill up data with defaults from model
        """
        # pylint: disable=not-callable
        model = self.model()
        for field in model._meta.get_fields():
            if field.name not in data and hasattr(field, 'default'):
                if field.default != NOT_PROVIDED:
                    if callable(field.default):
                        data[field.name] = field.default()
                    else:
                        data[field.name] = field.default
        return data

    def resolve_foreign_key(self, data):
        """
        Check for fields which are ForeignKey and resolve pk to instance
        """
        # pylint: disable=not-callable
        model = self.model()
        for field in model._meta.get_fields():
            # pylint: disable=unidiomatic-typecheck
            if type(field) == models.fields.related.ForeignKey:
                rev_match = field.target_field.model.objects.filter(pk=data[field.name])
                if not rev_match.exists():
                    raise Http404
                data[field.name] = rev_match.first()
        return data

    # pylint: disable=unused-argument
    def create(self, request, data):
        """
        Create instance based on request data
        """
        # Make sure only allowed fields are present
        sanitized = ModelAPI.sanitize_data(data, self.editable_fields)
        # # Fill data with model default data
        # sanitized = self.fill_with_defaults(sanitized)
        # Resolve foreign keys
        sanitized = self.resolve_foreign_key(sanitized)
        # # Check if all necessary keys are existent
        # self.check_keys(sanitized, self.editable_fields)
        inst = self.model.objects.create(**sanitized)
        return self.model_to_dict([inst, ])

    def read(self, request, data):
        """
        Show list of models
        """
        # Make sure only allowed fields are present
        sanitized = ModelAPI.sanitize_data(data, self.queryable_fields)
        all_instances = self.model.objects.filter(**sanitized)
        # Filter after user
        filtered = ModelAPI.user_filter(all_instances, request.user)
        return self.model_to_dict(filtered)

    def update(self, request, data):
        """
        Update model based on pk parameter
        """
        # Check if primary key is set
        if 'pk' not in data:
            raise Http404
        # Filter after user
        inst = ModelAPI.user_filter(self.model.objects.filter(pk=data['pk']), request.user)
        if not inst.exists():
            raise Http404
        r_inst = inst.first()
        # Make sure only allowed fields are present
        update_data = ModelAPI.sanitize_data(data, self.editable_fields)
        # Resolve foreign keys
        update_data = self.resolve_foreign_key(update_data)
        # # Check if all necessary keys are existent
        # self.check_keys(update_data, self.editable_fields)
        for key, value in update_data.items():
            setattr(r_inst, key, value)
        r_inst.save()
        return self.model_to_dict([r_inst, ])

    def delete(self, request, data):
        """
        Delete model instance
        """
        # Check if primary key is set
        if 'pk' not in data:
            raise Http404
        # Filter after user
        inst = ModelAPI.user_filter(self.model.objects.filter(pk=data['pk']), request.user)
        if not inst.exists():
            raise Http404
        r_inst = inst.first()
        r_inst.delete()
        return {'success': True}

class ProductAPI(ModelAPI):
    """
    ModelAPI optimized for Product-based Models
    """

    model = Product

    def create(self, request, data):
        """
        Create instance based on request data
        """
        orig = super(ProductAPI, self).create(request, data)
        prod = list(orig.values())[0]
        UserProductRelationship.objects.create(
            product=prod,
            user=request.user)
        return orig
