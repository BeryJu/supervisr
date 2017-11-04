"""
Supervisr Core Forms
"""
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import Setting


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
