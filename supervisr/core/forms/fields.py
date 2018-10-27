"""supervisr core form fields"""

from django.forms import ChoiceField, ValidationError

STATUS_CHOICE_SUCCESS = 'success'
STATUS_CHOICE_WARNING = 'warning'
STATUS_CHOICE_ERROR = 'error'



class StatusField(ChoiceField):
    """Field to show one of three different statuses"""

    minimum = None
    recommended = None
    current = None
    below_minimum_message = 'Current below minimum requirement.'

    def __init__(self, minimum=None, recommended=None, current=None, **kwargs):
        kwargs.update({
            'required': False
        })
        super().__init__(choices=(
            (STATUS_CHOICE_SUCCESS, STATUS_CHOICE_SUCCESS),
            (STATUS_CHOICE_WARNING, STATUS_CHOICE_WARNING),
            (STATUS_CHOICE_ERROR, STATUS_CHOICE_ERROR),
        ), **kwargs)
        self.minimum = minimum
        self.recommended = recommended
        self.current = current

    def clean(self, value=''):
        if self.current < self.minimum:
            value = STATUS_CHOICE_ERROR
        elif self.current < self.recommended:
            value = STATUS_CHOICE_WARNING
        else:
            value = STATUS_CHOICE_SUCCESS
        return super().clean(value)
