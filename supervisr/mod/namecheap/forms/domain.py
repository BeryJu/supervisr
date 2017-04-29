

from django import forms


class DoaminForm(forms.Form):

    title = _('Additional Information')

    domain = forms.CharField(label='Domain')
    first_name = forms.TextField()
    last_name = forms.TextField()
    address_1 = forms.TextField()
    city = forms.TextField()
    state_province = forms.TextField()
    postal_code = forms.TextField()
    country = forms.TextField()
    phone = forms.TextField()
