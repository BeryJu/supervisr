from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from ..ldap_connector import LDAPConnector
from ..forms.account import AuthenticationForm, SignupForm
import logging
logger = logging.getLogger(__name__)

def login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password'))
            if user is not None:
                django_login(req, user)
                messages.success(req, _("Successfully logged in!"))
                logger.info("Successfully logged in %s" % form.cleaned_data.get('email'))
                return redirect(reverse('common-index'))
            else:
                messages.error(req, _("Invalid Login"))
                logger.info("Failed to log in %s" % form.cleaned_data.get('email'))
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
                username=form.cleaned_data.get('email'),
                email=form.cleaned_data.get('email'),
                first_name=form.cleaned_data.get('name'))
            new_d_user.save()
            new_d_user.is_active = True
            new_d_user.set_password(form.cleaned_data.get('password'))
            new_d_user.save()
            # Create LDAP user if LDAP is active
            if LDAPConnector.enabled():
                ldap = LDAPConnector()
                ldap.create_user(new_d_user,
                    form.cleaned_data.get('password'))
            logger.info("Successfully signed up %s" % form.cleaned_data.get('email'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'account/signup.html', { 'form': form })
