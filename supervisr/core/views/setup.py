"""supervisr core initial_setup views"""
from logging import getLogger

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management.sql import emit_post_migrate_signal
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ModelState
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext as _

from supervisr.core.forms.setup import (AdminUserForm, PostInstallForm,
                                        PostSetupForm, PreInstallForm,
                                        RedisConnectivityForm,
                                        SystemRequirementsForm, WelcomeForm)
from supervisr.core.models import Setting, User
from supervisr.core.utils import is_database_synchronized
from supervisr.core.views.accounts import LoginView, SignupView
from supervisr.core.views.generic import AnonymousRequiredMixin
from supervisr.core.views.wizards import NamedWizard

LOGGER = getLogger(__name__)

# pylint: disable=unused-argument
def user_step_condition(wizard):
    """Returns True if new user should be created, otherwise False"""
    # Only show new user form if initial setup.
    # This errors out on first install as there are no tables yet, so we catch that as well
    try:
        return len(User.objects.all()) == 1
    except OperationalError:
        return True

class SetupWizard(AnonymousRequiredMixin, NamedWizard):
    """Setup to set branding, URL and other settings."""

    form_list = [
        ('welcome', WelcomeForm),
        ('system-requirements', SystemRequirementsForm),
        ('redis-connectivity', RedisConnectivityForm),
        # ('updates', UpdateForm),
        ('pre-install', PreInstallForm),
        ('post-install', PostInstallForm),
        ('user-setup', AdminUserForm),
        ('post-setup', PostSetupForm),
    ]
    template_list = {
        'welcome': '_admin/setup/welcome.html',
        'system-requirements': '_admin/setup/system_requirements.html',
        'redis-connectivity': '_admin/setup/redis_connectivity.html',
        'updates': '_admin/setup/updates.html',
        'pre-install': '_admin/setup/pre_install.html',
        'post-install': '_admin/setup/post_install.html',
        'user-setup': '_admin/setup/admin_user.html',
        'post-setup': '_admin/setup/post_setup.html',
    }
    condition_dict = {
        'user-setup': user_step_condition
    }
    title = _('Welcome to supervisr!')
    wizard_size = 'xl'
    migration_progress = {}
    __should_create_user = False

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        form = super().get_form(step, data, files)
        if isinstance(form, AdminUserForm):
            return form
        # Since most forms autopopulate data, re-instantiate them with
        # data={} to force them to clean
        form_class = form.__class__
        new_instance = form_class(data={})
        new_instance.is_valid()
        return new_instance

    def get_template_names(self):
        return [self.template_list[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'post-install':
            self.run_migrate()
            context['migration_status'] = self.migration_progress
        # Store state of install for template so we can show different texts for fresh installs
        # vs upgrades
        context['is_upgrade'] = not user_step_condition(self)
        return context

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Check if this is actually a fresh install, otherwise skip setup"""
        if is_database_synchronized() and not settings.TEST:
            # If database has been migrated already, check if we're still fresh installed or not
            if not Setting.get_bool('setup:is_fresh_install'):
                return redirect(reverse('common-index'))
        return super().dispatch(request, *args, **kwargs)

    def finish(self, form_list) -> HttpResponse:
        # Get AdminUserForm
        user_form = next(iter([form for form in form_list if isinstance(form, AdminUserForm)]),
                         None)
        if user_form:
            # re-use SignupView's create_user
            user = SignupView.create_user(user_form.cleaned_data, request=self.request,
                                          needs_confirmation=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            # User needs to be re-authenticated to fix backend errors
            auth_user = authenticate(
                email=user_form.cleaned_data.get('email'),
                password=user_form.cleaned_data.get('password'),
                request=self.request)
            # re-use LoginView's handle_login
            LoginView.handle_login(self.request, auth_user, user_form.cleaned_data)
        # no longer a fresh install
        Setting.set('setup:is_fresh_install', False)
        return redirect(reverse('common-index'))

    def run_migrate(self, db_alias=DEFAULT_DB_ALIAS) -> dict:
        """Apply Django Migrations"""
        # Get the database we're operating from
        connection = connections[db_alias]

        # Hook for backends needing any database preparation
        connection.prepare_database()
        # Work out which apps have migrations and which do not
        executor = MigrationExecutor(connection, self.migration_progress_callback)

        # Raise an error if any migrations are applied before their dependencies.
        executor.loader.check_consistent_history(connection)

        targets = executor.loader.graph.leaf_nodes()

        plan = executor.migration_plan(targets)

        # pylint: disable=protected-access
        pre_migrate_state = executor._create_project_state(with_applied_migrations=True)
        post_migrate_state = executor.migrate(
            targets, plan=plan, state=pre_migrate_state.clone(), fake=False,
            fake_initial=False,
        )
        # post_migrate signals have access to all models. Ensure that all models
        # are reloaded in case any are delayed.
        post_migrate_state.clear_delayed_apps_cache()
        post_migrate_apps = post_migrate_state.apps

        # Re-render models of real apps to include relationships now that
        # we've got a final state. This wouldn't be necessary if real apps
        # models were rendered with relationships in the first place.
        with post_migrate_apps.bulk_update():
            model_keys = []
            for model_state in post_migrate_apps.real_models:
                model_key = model_state.app_label, model_state.name_lower
                model_keys.append(model_key)
                post_migrate_apps.unregister_model(*model_key)
        post_migrate_apps.render_multiple([
            ModelState.from_model(apps.get_model(*model)) for model in model_keys
        ])

        # Send the post_migrate signal, so individual apps can do whatever they need
        # to do at this point.
        emit_post_migrate_signal(
            verbosity=0, interactive=False, db=connection.alias, apps=post_migrate_apps, plan=plan,
        )
        return self.migration_progress

    # pylint: disable=unused-argument
    def migration_progress_callback(self, action, migration=None, fake=False):
        """Save Progress"""
        if action == "apply_start":
            self.migration_progress[migration] = ''
            LOGGER.info("Started %s", migration)
        elif action == "apply_success":
            self.migration_progress[migration] = 'success'
            LOGGER.success("Succeeded %s", migration)
