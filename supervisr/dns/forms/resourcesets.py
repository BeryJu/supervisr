"""Supervisr DNS ResourceSet Forms"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.dns.models import ResourceSet


class ResourceSetForm(forms.ModelForm):
    """Create/edit ResourceSetForm"""

    title = _('General Information')

    class Meta:

        model = ResourceSet
        fields = ['name', 'resource']
        widgets = {
            'name': forms.TextInput(),
        }
