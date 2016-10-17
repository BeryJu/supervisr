from django import forms

class AccountAuthenticationForm(forms.Form):
    mail = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

