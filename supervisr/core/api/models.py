"""
Supervisr Core r1 Model API
"""
import collections

from django import forms
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.http import Http404

from supervisr.core.api.crud import CRUDAPI
from supervisr.core.models import UserAcquirable, UserAcquirableRelationship


class ModelAPI(CRUDAPI):
    """Basic API for Models"""

    model = None
    form = None

    queryable_fields = ['name']
    viewable_fields = ['name']
    editable_fields = ['name']

    def pre_handler(self, handler, request):
        """Check if form is set and read fields from it"""
        if self.form:
            # Wrapper for single form APIs
            if not isinstance(self.form, collections.Sequence):
                self.form = [self.form]
            new_fields = []
            for frm in self.form:
                frm_inst = frm()
                if isinstance(frm_inst, forms.ModelForm):
                    if getattr(frm_inst.Meta, 'fields', None):
                        # Add stated fields
                        fields = frm_inst.Meta.fields
                    elif getattr(frm_inst.Meta, 'exclude', None):
                        # Remove excluded fields from model
                        model = frm_inst.Meta.model
                        fields = [x.name for x in model._meta.get_fields()
                                  if x.name not in frm_inst.Meta.exclude]
                    # Add all fields from all arrays into our fields
                    new_fields += fields
            # convert concatenated list into set to remove duplicates
            new_fields = set(new_fields)
            self.queryable_fields = new_fields
            self.viewable_fields = new_fields
            self.editable_fields = new_fields
            return True
        return False

    @staticmethod
    def user_filter(queryset, user):
        """This method is used to check if the user has access"""
        if not user.is_authenticated:
            raise PermissionDenied
        return queryset

    def model_to_dict(self, qs):
        """Convert queryset to dict"""
        final_arr = []
        for m_inst in qs:
            inst_dict = {'pk': m_inst.pk}
            for field in self.viewable_fields:
                data = getattr(m_inst, field, None)
                if isinstance(data, models.Model):
                    data = data.pk
                inst_dict[field] = data
            final_arr.append(inst_dict)
        return final_arr

    @staticmethod
    def sanitize_data(data, keyset):
        """Sanitize data with keyset"""
        new_data = {}
        for key, value in data.items():
            if key in keyset:
                new_data[key] = value
        return new_data

    @staticmethod
    def check_keys(data, keyset):
        """Check if data has all keys it should have"""
        for key in keyset:
            if key not in data:
                raise KeyError('Key %s not in data' % key)
        return True

    def fill_with_defaults(self, data):
        """Fill up data with defaults from model"""
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
        """Check for fields which are ForeignKey and resolve pk to instance"""
        # pylint: disable=not-callable
        model = self.model()
        for field in model._meta.get_fields():
            # pylint: disable=unidiomatic-typecheck
            if type(field) == models.fields.related.ForeignKey:
                rev_match = field.target_field.model.objects.filter(pk=data[field.name])
                if not rev_match.exists():
                    raise Http404
                assert len(rev_match) == 1
                data[field.name] = rev_match.first()
        return data

    def create(self, request, data):
        """Create instance based on request data"""
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
        """Show list of models"""
        # Make sure only allowed fields are present
        sanitized = ModelAPI.sanitize_data(data, self.queryable_fields)
        all_instances = self.model.objects.filter(**sanitized)
        # Filter after user
        filtered = ModelAPI.user_filter(all_instances, request.user)
        return self.model_to_dict(filtered)

    def update(self, request, data):
        """Update model based on pk parameter"""
        # Check if primary key is set
        if 'pk' not in data:
            raise Http404
        # Filter after user
        inst = ModelAPI.user_filter(self.model.objects.filter(pk=data['pk']), request.user)
        if not inst.exists():
            raise Http404
        assert len(inst) == 1
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
        """Delete model instance"""
        # Check if primary key is set
        if 'pk' not in data:
            raise Http404
        # Filter after user
        inst = ModelAPI.user_filter(self.model.objects.filter(pk=data['pk']), request.user)
        if not inst.exists():
            raise Http404
        assert len(inst) == 1
        r_inst = inst.first()
        r_inst.delete()
        return {'success': True}

class UserAcquirableModelAPI(ModelAPI):
    """ModelAPI optimized for UserAcquirable Models"""

    model = UserAcquirable

    def create(self, request, data):
        """Create instance based on request data"""
        original = super(UserAcquirableModelAPI, self).create(request, data)
        model = original[0]
        UserAcquirableRelationship.objects.create(
            model=model,
            user=request.user)
        return original
