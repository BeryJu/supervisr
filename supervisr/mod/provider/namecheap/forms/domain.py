"""
Supervisr Mod Namecheap Domain Forms
"""

from django import forms
from django.utils.translation import ugettext as _


class DoaminForm(forms.Form):
    """
    Namecheap Domain Creation form
    """

    title = _('Additional Information')

    domain = forms.CharField(label='Domain')
    first_name = forms.CharField()
    last_name = forms.CharField()
    address_1 = forms.CharField()
    city = forms.CharField()
    state_province = forms.CharField()
    postal_code = forms.CharField()
    country = forms.CharField()
    phone = forms.CharField()
