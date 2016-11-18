from django import forms

class AuthenticationForm(forms.Form):
    mail = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField()
