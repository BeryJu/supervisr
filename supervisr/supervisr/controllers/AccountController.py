from django.contrib.auth.models import User
from ..ldap_connector import LDAPConnector
from ..forms.account import AuthenticationForm, SignupForm, ChangePasswordForm
from ..models import AccountConfirmation, UserProfile
from ..mailer import Mailer
import logging
logger = logging.getLogger(__name__)

def signup(email, name, password):
    # Create django user
    new_d_user = User.objects.create_user(
        username=email,
        email=email,
        first_name=name)
    new_d_user.save()
    new_d_user.is_active = False
    new_d_user.set_password(password)
    new_d_user.save()
    # Create user profile
    new_up = UserProfile(user=new_d_user)
    new_up.save()
    # Create LDAP user if LDAP is active
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        # Returns false if user could not be created
        if not ldap.create_user(new_d_user, password):
            # Add message what happend and return
            messages.error(req, _("Failed to create user"))
            new_d_user.delete()
            return False
        ldap.disable_user(new_d_user.email)
    # Send confirmation email
    ac = AccountConfirmation(user=new_d_user)
    ac.save()
    # Send confirmation mail
    Mailer.send_account_confirmation(new_d_user.email, ac)
    return True

def change_password(email, password):
    # Change Django password
    u = User.objects.get(pk=email)
    u.set_password(password)
    u.save()
    # Update ldap password if LDAP is enabled
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        ldap.change_password(email, password)
    logger.debug("Successfully updated password for %s" % email)
    return True