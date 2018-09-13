"""Supervisr PowerDNS DB Router"""


class PowerDNSRouter(object):
    """
    A router to control all database operations on models in the
    PowerDNS application.
    """

    # pylint: disable=unused-argument
    def db_for_read(self, model, **hints):
        """Attempts to read auth models go to PowerDNS."""
        if model._meta.app_label == 'supervisr_mod_provider_nix_dns':
            return 'powerdns'
        return None

    # pylint: disable=unused-argument
    def db_for_write(self, model, **hints):
        """Attempts to write auth models go to PowerDNS."""
        if model._meta.app_label == 'supervisr_mod_provider_nix_dns':
            return 'powerdns'
        return None

    # pylint: disable=unused-argument
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a model in the auth app is involved."""
        if obj1._meta.app_label == 'supervisr_mod_provider_nix_dns' or \
           obj2._meta.app_label == 'supervisr_mod_provider_nix_dns':
            return True
        return None

    # pylint: disable=unused-argument, invalid-name
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure the auth app only appears in the 'PowerDNS' database."""
        if db == 'powerdns':
            return app_label == 'supervisr_mod_provider_nix_dns'
        return None
