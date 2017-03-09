"""
Supervisr Core Forms
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms


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
