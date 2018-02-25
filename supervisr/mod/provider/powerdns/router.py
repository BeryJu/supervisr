"""Supervisr PowerDNS DB Router"""

from django.conf import settings


class PowerDNSRouter(object):
    """
    A router to control all database operations on models in the
    PowerDNS application.
    """

    def __init__(self):
        """
        Check if there's a seperate PowerDNS Database
        """
        # Try different names for PDNS database, fall back to default
        for name in ['powerdns', 'pdns', 'dns', 'default']:
            if name in settings.DATABASES:
                self._db = name

    # pylint: disable=unused-argument, no-self-use
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to PowerDNS.
        """
        if model._meta.app_label == 'supervisr_mod_provider_powerdns':
            return self._db
        return None

    # pylint: disable=unused-argument, no-self-use
    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to PowerDNS.
        """
        if model._meta.app_label == 'supervisr_mod_provider_powerdns':
            return self._db
        return None

    # pylint: disable=unused-argument, no-self-use
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'supervisr_mod_provider_powerdns' or \
           obj2._meta.app_label == 'supervisr_mod_provider_powerdns':
            return True
        return None

    # pylint: disable=unused-argument, no-self-use, invalid-name
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'PowerDNS'
        database.
        """
        if app_label == 'supervisr_mod_provider_powerdns':
            return db == self._db
        return None
