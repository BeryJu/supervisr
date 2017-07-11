"""
Supervisr Mail MultiEmail Field (based on Textarea)
"""
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _


class MultiEmailField(forms.Field):
    """
    Email field for multiple emails
    """
    message = _('Enter valid email addresses.')
    code = 'invalid'
    widget = Textarea

    def to_python(self, value):
        "Normalize data to a list of strings."
        # Return None if no input was given.
        if not value:
            return []
        return [v.strip() for v in value.splitlines() if v != ""]

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)
        try:
            for email in value:
                validate_email(email)
        except ValidationError:
            raise ValidationError(self.message, code=self.code)
