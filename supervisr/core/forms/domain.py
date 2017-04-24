"""
Supervisr Core Domain Forms
"""


from django import forms


class NewDomainForm(forms.Form):
    """
    Form create a new Domain
    """

    title = 'General Information'

    domain = forms.CharField(label='Domain')
    registrar = forms.CharField(label='Registrar')
