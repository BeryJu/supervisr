from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from ..ldap_connector import LDAPConnector
from ..forms.account import AuthenticationForm, SignupForm

def login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('mail'),
                password=form.cleaned_data.get('password'))
            if user is not None:
                login(req, user)
                messages.success(req, _("Successfully logged in!"))
                return redirect(reverse('common-index'))
            else:
                messages.error(req, _("Invalid Login"))
                return redirect(reverse('account-login'))
    else:
        form = AuthenticationForm()
    return render(req, 'account/login.html', { 'form': form })

def signup(req):
    if req.method == 'POST':
        form = SignupForm(req.POST)
        if form.is_valid():
            # Create django user
            new_d_user = User.objects.create_user(
                username=form.cleaned_data.get('mail'),
                email=form.cleaned_data.get('mail'),
                password=form.cleaned_data.get('password'))
            # Create LDAP user if LDAP is active
            if LDAPConnector.enabled():
                ldap = LDAPConnector()
                ldap.bind()
                ldap.create_user(new_d_user,
                    form.cleaned_data.get('password'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'account/login.html', { 'form': form })
