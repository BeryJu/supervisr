"""
Supervisr Core Account Views
"""

import logging
import time
from typing import Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.http import require_GET
from passlib.hash import sha512_crypt

from supervisr.core.decorators import anonymous_required, require_setting
from supervisr.core.forms.accounts import (ChangePasswordForm,
                                           EmailMissingForm, LoginForm,
                                           PasswordResetFinishForm,
                                           PasswordResetInitForm, ReauthForm,
                                           SignupForm)
from supervisr.core.models import (AccountConfirmation, Setting, User,
                                   make_username)
from supervisr.core.signals import (SIG_USER_CHANGE_PASS, SIG_USER_CONFIRM,
                                    SIG_USER_PASS_RESET_INIT,
                                    SIG_USER_POST_CHANGE_PASS,
                                    SIG_USER_POST_SIGN_UP,
                                    SIG_USER_RESEND_CONFIRM, SIG_USER_SIGN_UP,
                                    SignalException)

LOGGER = logging.getLogger(__name__)

@method_decorator(anonymous_required, name='dispatch')
class LoginView(View):
    """View to handle login logic"""

    def render(self, request: HttpRequest, form: LoginForm) -> HttpResponse:
        """Render our template

        Args:
            request: The current request

        Returns:
            Login template
        """
        extra_links = {}
        if Setting.get_bool('password_reset:enabled'):
            extra_links['account-reset_password_init'] = 'Reset your password'
        if Setting.get_bool('signup:enabled'):
            extra_links['account-signup'] = 'Sign up for an account'
        return render(request, 'account/login.html', {
            'form': form,
            'title': _("SSO - Login"),
            'primary_action': _("Login"),
            'extra_links': extra_links
            })

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle Get request

        Args:
            request: The current request

        Returns:
            Login template
        """
        form = LoginForm()
        return self.render(request, form)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request

        Args:
            request: The current request

        Returns:
            Either a redirect to next view or login template if any errors exist
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password'),
                request=request)
            if user:
                return self.handle_login(request, user, form.cleaned_data)
            return self.handle_disabled_login(request, email=form.cleaned_data.get('email'))
        LOGGER.debug("LoginForm invalid")
        return self.render(request, form=form)

    def handle_login(self, request: HttpRequest, user: User, cleaned_data: Dict) -> HttpResponse:
        """Handle actual login

        Actually logs user in, sets session expiry and redirects to ?next parameter

        Args:
            request: The current request
            user: The user to be logged in.

        Returns:
            Either redirect to ?next or if not present to common-index
        """
        assert user is not None
        django_login(request, user)
        # Set updated password in user profile for PAM
        user.crypt6_password = \
            sha512_crypt.hash(cleaned_data.get('password'))
        user.save()

        if cleaned_data.get('remember') is True:
            request.session.set_expiry(settings.REMEMBER_SESSION_AGE)
        else:
            request.session.set_expiry(0) # Expires when browser is closed
        messages.success(request, _("Successfully logged in!"))
        # Send event that we're logged in now
        user_logged_in.send(
            sender=self, user=user, request=request)
        LOGGER.debug("Successfully logged in %s", user.username)
        # Check if there is a next GET parameter and redirect to that
        if 'next' in request.GET:
            return redirect(request.GET.get('next'))
        # Otherwise just index
        return redirect(reverse('common-index'))

    def handle_disabled_login(self, request: HttpRequest, email: str) -> HttpResponse:
        """Handle login for disabled users

        This informs users that their email is not confirmed yet

        Args:
            request: The current request
            email: email to search the user by

        Returns:
            Either redirect to ?next or if not present to common-index
        """
        # Check if the user's account is pending
        # and inform that, they need to check their emails
        users = User.objects.filter(email=email)
        if users.exists() and not users.first().is_active:
            # Check is maybe not confirmed yet
            acc_confs = AccountConfirmation.objects.filter(
                user=users.first(),
                kind=AccountConfirmation.KIND_SIGN_UP)
            if acc_confs.exists() and not acc_confs.first().confirmed:
                # Create url to resend email
                url = reverse('account-confirmation_resend',
                              kwargs={'email': users.first().email})
                messages.error(request, _(('Account not confirmed yet. Check your emails. '
                                           'Click <a href="%(url)s">here</a> to resend the '
                                           'email.')) % {'url': url})
                return redirect(reverse('account-login'))
        messages.error(request, _("Invalid Login"))
        LOGGER.debug("Failed to log in %s", email)
        return redirect(reverse('account-login'))

@method_decorator(anonymous_required, name='dispatch')
@method_decorator(require_setting('supervisr.core/signup:enabled', True), name='dispatch')
class SignupView(View):
    """View to handle Signup requests"""

    def render(self, request: HttpRequest, form: LoginForm) -> HttpResponse:
        """Render our template

        Args:
            request: The current request

        Returns:
            Login template
        """
        return render(request, 'core/generic_form_login.html', {
            'form': form,
            'title': _("SSO - Signup"),
            'primary_action': _("Signup")
            })

    def create_user(self, data: Dict, request: HttpRequest = None) -> User:
        """Create user from data

        Args:
            data: Dictionary as returned by SignupForm's cleaned_data
            request: Optional current request.

        Returns:
            The user created

        Raises:
            SignalException: if any signals raise an exception. This also deletes the created user.
        """
        # Create user
        new_user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('name'),
            crypt6_password=sha512_crypt.hash(data.get('password')),
            unix_username=make_username(data.get('username'))
            )
        new_user.is_active = False
        new_user.set_password(data.get('password'))
        new_user.save()
        # Send signal for other auth sources
        try:
            SIG_USER_SIGN_UP.send(
                sender=None,
                user=new_user,
                request=request,
                password=data.get('password'))
            # Create Account Confirmation UUID
            AccountConfirmation.objects.create(user=new_user)
            # Send event for user creation
            SIG_USER_POST_SIGN_UP.send(
                sender=None,
                user=new_user,
                request=request)
        except SignalException as exception:
            LOGGER.warning("Failed to sign up user %s", exception)
            new_user.delete()
            raise
        return new_user

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request

        Args:
            request: The current HttpRequest

        Returns:
            Either the signup form if any errors exist, otherwise redirect to common-index
        """
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                self.create_user(form.cleaned_data, request)
                messages.success(request, _("Successfully signed up!"))
                LOGGER.debug("Successfully signed up %s",
                             form.cleaned_data.get('email'))
                return redirect(reverse('account-login'))
            except SignalException:
                messages.error(request, _("Failed to sign up."))
        return self.render(request, form)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle Get request

        Args:
            request: The Current HttpRequest

        Returns:
            Rendered signup form
        """
        form = SignupForm()
        return self.render(request, form)

@login_required
def change_password(request):
    """
    View to handle Browser change_password Requests
    """
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            # Change Django password
            request.user.set_password(form.cleaned_data.get('password'))
            request.user.save()
            try:
                # Send signal for other auth sources
                SIG_USER_CHANGE_PASS.send(
                    sender=None,
                    user=request.user,
                    request=request,
                    password=form.cleaned_data.get('password'))
                # Trigger Event
                SIG_USER_POST_CHANGE_PASS.send(
                    sender=None,
                    user=request.user,
                    was_reset=False,
                    request=request)
                LOGGER.debug("Successfully updated password for %s", request.user.email)
                messages.success(request, _("Successfully changed password!"))
            except SignalException as exception:
                messages.error(request, _("Failed to change password"))
                LOGGER.warning(exception)
            return redirect(reverse('common-index'))
    else:
        form = ChangePasswordForm()
    return render(request, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Change Password"),
        'primary_action': _("Change Password")
        })

@login_required
@require_GET
def logout(request):
    """View to handle Browser logout Requests"""
    # Send event first because we still have the user
    user_logged_out.send(
        sender=logout, user=request.user, request=request)
    django_logout(request)
    messages.success(request, _("Successfully logged out!"))
    return redirect(reverse('common-index'))

@anonymous_required
@require_GET
def confirm(request, uuid):
    """View to handle Browser account_confirm Requests"""
    if AccountConfirmation.objects.filter(
            pk=uuid,
            kind=AccountConfirmation.KIND_SIGN_UP).exists():
        acc_conf = AccountConfirmation.objects.get(pk=uuid)
        if acc_conf.confirmed:
            messages.error(request, _("Account already confirmed!"))
            return redirect(reverse('account-login'))
        if acc_conf.is_expired:
            messages.error(request, _("Confirmation expired"))
            return redirect(reverse('account-login'))
        # activate django user
        acc_conf.user.is_active = True
        acc_conf.user.save()
        # Send signal to other auth sources
        SIG_USER_CONFIRM.send(
            sender=None,
            user=acc_conf.user,
            request=request)
        # invalidate confirmation
        acc_conf.confirmed = True
        acc_conf.save()
        messages.success(request, _("Account successfully activated!"))
    else:
        raise Http404
    return redirect(reverse('account-login'))

@anonymous_required
@require_setting('supervisr.core/password_reset:enabled', True)
def reset_password_init(request):
    """
    View to handle Browser account password reset initiation Requests
    """
    if request.method == 'POST':
        form = PasswordResetInitForm(request.POST)
        if form.is_valid():
            users = User.objects.filter(email=form.cleaned_data.get('email'))
            if users.exists():
                r_user = users.first()
                AccountConfirmation.objects.create(
                    user=r_user,
                    kind=AccountConfirmation.KIND_PASSWORD_RESET)
                SIG_USER_PASS_RESET_INIT.send(
                    sender=reset_password_init, user=r_user)
            messages.success(request, _('Reset link sent successfully if user exists.'))
    else:
        form = PasswordResetInitForm()
    return render(request, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Reset your password - Step 1/3"),
        'primary_action': _("Send confirmation Email")
        })

@anonymous_required
@require_setting('supervisr.core/password_reset:enabled', True)
def reset_password_confirm(request, uuid):
    """
    View to handle Browser account password reset confirmation Requests
    """
    if request.method == 'POST':
        form = PasswordResetFinishForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if AccountConfirmation.objects.filter(
                    pk=uuid,
                    kind=AccountConfirmation.KIND_PASSWORD_RESET).exists():
                pass_conf = AccountConfirmation.objects.get(pk=uuid)
                if pass_conf.confirmed:
                    messages.error(request, _("Link already used!"))
                    return redirect(reverse('account-login'))
                if pass_conf.is_expired:
                    messages.error(request, _("Link expired!"))
                    return redirect(reverse('account-login'))
                # Change Django password
                pass_conf.user.set_password(password)
                pass_conf.user.save()
                try:
                    # Send signal for other auth sources
                    SIG_USER_CHANGE_PASS.send(
                        sender=None,
                        user=pass_conf.user,
                        request=request,
                        password=password)
                    # Trigger Event
                    SIG_USER_POST_CHANGE_PASS.send(
                        sender=None,
                        user=pass_conf.user,
                        was_reset=True,
                        request=request)
                    LOGGER.debug("Successfully updated password for %s", pass_conf.user.email)
                    messages.success(request, _("Account successfully reset!"))
                    # invalidate confirmation
                    pass_conf.confirmed = True
                    pass_conf.save()
                except SignalException as exception:
                    LOGGER.warning(exception)
                    messages.error(request, _("Failed to reset Password. Please try again later."))
            else:
                raise Http404
            return redirect(reverse('account-login'))
    else:
        form = PasswordResetFinishForm()
    return render(request, 'core/generic_form_login.html', {
        'form': form,
        'title': _("SSO - Reset your Password - Step 3/3"),
        'primary_action': _("Reset your Password")
        })

@method_decorator(require_GET, name='dispatch')
@method_decorator(anonymous_required, name='dispatch')
class ConfirmationResendView(View):
    """View to resend E-Mail confirmation requests"""

    def get(self, request: HttpRequest, email: str) -> HttpResponse:
        """Handle request"""
        users = User.objects.filter(email=email, is_active=False)
        if users.exists():
            # Invalidate all other links for this user
            old_acs = AccountConfirmation.objects.filter(
                user=users.first())
            for old_ac in old_acs:
                old_ac.confirmed = True
                old_ac.save()
            # Create Account Confirmation UUID
            AccountConfirmation.objects.create(user=users.first())
            SIG_USER_RESEND_CONFIRM.send(
                sender=None,
                user=users.first(),
                request=request)
            messages.success(request, _("Successfully resent confirmation email"))
            return redirect(reverse('account-login'))
        raise Http404

@method_decorator(login_required, name='dispatch')
class ReauthView(View):
    """View to re-authenticate user before important actions"""

    def render(self, request: HttpRequest, form: ReauthForm) -> HttpResponse:
        """Render form"""
        return render(request, 'core/generic_form_login.html', {
            'form': form,
            'title': _("SSO - Re-Authenticate"),
            'primary_action': _("Login"),
            })

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request to validate password"""
        form = ReauthForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=request.user.email,
                password=form.cleaned_data.get('password'),
                request=request)
            if user == request.user:
                messages.success(request, _('Successfully Re-Authenticated'))
                request.session['supervisr_require_reauth_done'] = time.time()
                # Check if there is a next GET parameter and redirect to that
                if 'next' in request.GET:
                    return redirect(request.GET.get('next'))
                # Otherwise just index
                return redirect(reverse('common-index'))
        messages.error(request, _('Failed to Re-Authenticate'))
        return self.render(request, form)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Show Form"""
        form = ReauthForm(initial={'email': request.user.email})
        return self.render(request, form)

@method_decorator(anonymous_required, name='dispatch')
class EmailMissingView(View):
    """View to ask user for missing email"""

    def render(self, request: HttpRequest, form: EmailMissingForm) -> HttpResponse:
        """Render our template

        Args:
            request: The current request

        Returns:
            Login template
        """
        return render(request, 'account/login.html', {
            'form': form,
            'title': _("SSO - Add missing E-Mail"),
            'primary_action': _("Add"),
            })

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle Get request

        Args:
            request: The current request

        Returns:
            Login template
        """
        form = EmailMissingForm()
        return self.render(request, form)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle Post request

        Args:
            request: The current request

        Returns:
            Either a redirect to next view or login template if any errors exist
        """
        form = EmailMissingForm(request.POST)
        if form.is_valid():
            request.user.is_active = False
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            # Create new AccountConfirmation UUID set
            AccountConfirmation.objects.create(user=request.user)
            SIG_USER_RESEND_CONFIRM.send(
                sender=self,
                user=request.user,
                request=request
            )
            messages.success(request, _('Successfully sent confirmation E-Mail'))
            django_logout(request)
            return redirect(reverse('common-loign'))
        return self.render(request, form=form)
