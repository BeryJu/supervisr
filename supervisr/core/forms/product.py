"""Supervisr Core Product Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import Product


class ProductForm(forms.ModelForm):
    """Create/edit ProductForm"""

    title = _('General Information')

    class Meta:

        model = Product
        fields = ['name', 'slug', 'description', 'invite_only', 'auto_add',
                  'auto_all_add', 'managed', 'management_url', 'extensions']
        widgets = {
            'name': forms.TextInput(),
        }
