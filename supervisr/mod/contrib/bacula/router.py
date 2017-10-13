"""
Supervisr Bacula DB Router
"""

class BaculaRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """

    def __init__(self):
        """
        Check if there's a seperate Bacula Database
        """
        self._db = 'bacula'

    # pylint: disable=unused-argument, no-self-use
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to bacula.
        """
        if model._meta.app_label == 'supervisr/mod/contrib/bacula':
            return self._db
        return None

    # pylint: disable=unused-argument, no-self-use
    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to bacula.
        """
        if model._meta.app_label == 'supervisr/mod/contrib/bacula':
            return self._db
        return None

    # pylint: disable=unused-argument, no-self-use
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'supervisr/mod/contrib/bacula' or \
           obj2._meta.app_label == 'supervisr/mod/contrib/bacula':
            return True
        return None

    # pylint: disable=unused-argument, no-self-use, invalid-name
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'bacula'
        database.
        """
        if app_label == 'supervisr/mod/contrib/bacula':
            return db == self._db
        return None
