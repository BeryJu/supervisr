from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from ..forms.account import AuthenticationForm, SignupForm

def login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
        if form.is_valid():
            # authentication and ldap checking here
            return redirect(reverse('common-index'))
    else:
        form = AuthenticationForm()
    return render(req, 'account/login.html', { 'form': form })

def signup(req):
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.is_valid():
            # Account creation here
            return redirect(reverse('common-index'))
    else:
        form = SignupForm()
    return render(req, 'account/login.html', { 'form': form })
