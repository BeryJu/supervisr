"""Supervisr Core Product Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from supervisr.core.models import Product, ProductExtension


class ProductForm(forms.ModelForm):
    """Create/edit ProductForm"""

    title = _('General Information')

    class Meta:

        model = Product
        fields = ['name', 'slug', 'description', 'invite_only', 'auto_add', 'auto_all_add']
        widgets = {
            'name': forms.TextInput(),
        }
        help_texts = {
            'auto_add': _('Automatically add Product to new users.'),
            'auto_all_add': _('Automatically add Product to all users.')
        }


class ProductExtensionAssignForm(forms.Form):
    """Assign extensions for a Product Insatnce"""

    title = _('Assign Extensions')
    extensions = forms.ModelMultipleChoiceField(queryset=ProductExtension.objects.all())


class ProductExtensionForm(forms.ModelForm):
    """Generic Form for ProductExtensions"""

    title = _('Product Extension')

    class Meta:

        model = ProductExtension
        fields = '__all__'
