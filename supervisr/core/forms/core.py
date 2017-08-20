"""
Supervisr Core Forms
"""
import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.utils.translation import ugettext as _

from ..models import Setting


class InlineForm(forms.Form):
    """
    Form with a bootstrap3 inline template applied
    """

    order = []

    def __init__(self, *args, **kwargs):
        super(InlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(*self.order)

def check_password(form, check_filter=True):
    """
    Check if Password adheres to filter and if passwords matche
    """
    password_a = form.cleaned_data.get('password')
    password_b = form.cleaned_data.get('password_rep')
    # Check if either field is required.
    if form.fields['password'].required is False and \
        form.fields['password_rep'].required is False:
        return password_a
    # Error if one password is empty.
    if not password_b:
        raise forms.ValidationError(_("You must confirm your password"))
    if password_a != password_b:
        raise forms.ValidationError(_("Your passwords do not match"))
    # Check if password is strong enough
    if Setting.get('password:filter') != '' and check_filter:
        if not re.match(Setting.get('password:filter'), password_b):
            desc = Setting.get('password:filter:description')
            raise forms.ValidationError(_("Password has to contain %(desc)s" % {
                'desc': desc
                }))
    return password_a
