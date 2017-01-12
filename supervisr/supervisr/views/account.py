from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from ..ldap_connector import LDAPConnector
from ..forms.account import AuthenticationForm, SignupForm, ChangePasswordForm
from ..models import AccountConfirmation
import logging
import time
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
                if form.cleaned_data.get('remember') is True:
                    req.session.set_expiry(settings.REMEMBER_SESSION_AGE)
                else:
                    req.session.set_expiry(0) # Expires when browser is closed
                messages.success(req, _("Successfully logged in!"))
                logger.info("Successfully logged in %s" % form.cleaned_data.get('email'))
                return redirect(reverse('common-index'))
            else:
                # Check if the user's account is pending
                # and inform that, they need to check their emails
                user = User.objects.get(username=form.cleaned_data.get('email'))
                ac = AccountConfirmation.objects.get(user=user)
                if not ac.confirmed:
                    messages.error(req, _('Account not confirmed yet. Check your emails.'))
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
            new_d_user.is_active = False
            new_d_user.set_password(form.cleaned_data.get('password'))
            new_d_user.save()
            # Create user profile
            new_up = UserProfile(user=new_d_user)
            new_up.save()
            # Create LDAP user if LDAP is active
            if LDAPConnector.enabled():
                ldap = LDAPConnector()
                # Returns false if user could not be created
                if not ldap.create_user(new_d_user, \
                    form.cleaned_data.get('password')):
                    # Add message what happend and return
                    messages.error(req, _("Failed to create user"))
                    new_d_user.delete()
                    return redirect(reverse('account-login'))
                ldap.disable_user(new_d_user.email)
            # Send confirmation email
            ac = AccountConfirmation(user=new_d_user)
            ac.save()
            domain = Setting.objects.get('supervisr:domain').value
            url = domain + reverse('account-confirm',
                kwargs={'uuid': ac.pk})
            # get template and context
            template = loader.get_template('email/acount_confirm.html')
            ctx = Context({ 'url': url })
            send_mail(_("Confirm your account on BeryJu.org"), \
                '', settings.EMAIL_FROM, [new_d_user.email],
                fail_silently=False,
                html_message=template.render(ctx))
            logger.info("Successfully signed up %s" % \
                form.cleaned_data.get('email'))
            return redirect(reverse('account-login'))
    else:
        form = SignupForm()
    return render(req, 'account/signup.html', { 'form': form })

@login_required
def change_password(req):
    if req.method == 'POST':
        form = ChangePasswordForm(req.POST)
        if form.is_valid():
            # Change Django password
            req.user.set_password(form.cleaned_data.get('password'))
            # Update ldap password if LDAP is enabled
            if LDAPConnector.enabled():
                ldap = LDAPConnector()
                ldap.change_password(req.user.email,
                    form.cleaned_data.get('password'))
            logger.info("Successfully changed password for %s" \
                % form.cleaned_data.get('email'))
            messages.success(req, _("Successfully changed password!"))
            return redirect(reverse('common-index'))
    else:
        form = ChangePasswordForm()
    return render(req, 'account/change_password.html', { 'form': form })

@login_required
def logout(req):
    django_logout(req)
    messages.success(req, _("Successfully logged out!"))
    return redirect(reverse('common-index'))

def confirm(req, uuid):
    current_time = time.time()
    if AccountConfirmation.objects.filter(pk=uuid).exists():
        ac = AccountConfirmation.objects.get(pk=uuid)
        if ac.confirmed:
            messages.error(req, _("Account already confirmed!"))
            return redirect(reverse('account-login'))
        if not ac.is_expired():
            messages.error(req, _("Confirmation expired"))
            return redirect(reverse('account-login'))
        # activate django user
        ac.user.is_active = True
        ac.user.save()
        # activate LDAP user
        if LDAPConnector.enabled():
            ldap = LDAPConnector()
            ldap.enable_user(ac.user.email)
        # invalidate confirmation
        ac.confirmed = True
        ac.save()
        messages.success(req, _("Account successfully activated!"))
    else:
        messages.error(req, _("Confirmation not found"))
    return redirect(reverse('account-login'))
