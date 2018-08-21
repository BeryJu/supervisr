"""supervisr core initial_setup forms"""
import multiprocessing
from platform import python_version

from django import forms
from django.utils.translation import ugettext_lazy as _
from packaging import version
from psutil import virtual_memory

from supervisr.core.forms.accounts import SignupForm
from supervisr.core.forms.fields import StatusField
from supervisr.core.utils import check_redis_connection, get_db_server_version


class WelcomeForm(forms.Form):
    """Initial Form"""

    title = _('Welcome')


class SystemRequirementsForm(forms.Form):
    """System requirements Form.
    Checks are validated in this Form and are rendered with custom HTML"""

    title = _("System requirements")

    cpu_requirement = StatusField(minimum=1, recommended=2,
                                  current=multiprocessing.cpu_count(),
                                  help_text=_('CPU Requirements'))
    ram_requirement = StatusField(minimum=2, recommended=4,
                                  current=virtual_memory().total >> 30,
                                  help_text=_('RAM Requirements'))
    python_requirement = StatusField(minimum=version.parse('3.5'),
                                     recommended=version.parse('3.5'),
                                     current=version.parse(python_version()),
                                     help_text=_('Python Version Requirements'))
    db_requirement = StatusField(minimum=version.parse('8.0'),
                                 recommended=version.parse('10.0'),
                                 current=version.parse(get_db_server_version(default='99.0')),
                                 help_text=_('MySQL Version Requirement'))


class RedisConnectivityForm(forms.Form):
    """Check Redis connectivity"""

    title = _('Redis Connectivity')

    redis_connectivity = StatusField(minimum=True, recommended=True,
                                     current=check_redis_connection(),
                                     help_text=_('Redis Connectivity'))


class UpdateForm(forms.Form):
    """Update Form"""

    title = _("Updates")


class PreInstallForm(forms.Form):
    """Show quick information before triggering install"""

    title = _('Pre-install Summary')


class PostInstallForm(forms.Form):
    """Show summary of installed migrations"""

    title = _('Post-install Summary')


class AdminUserForm(SignupForm):
    """SignupForm with added title"""

    title = _('User Setup')


class PostSetupForm(forms.Form):
    """Show summary after setup and success message"""

    title = _('Installation completed!')
