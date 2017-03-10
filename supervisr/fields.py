"""
Supervisr Core Fields
"""

import json

from django.db import models


class JSONField(models.TextField):
    """
    Field to save json in DB, works on non-postgres
    """

    # pylint: disable=no-self-use, unused-argument
    def from_db_value(self, value, experssion, connection, context):
        """
        Convert JSON String to object
        """
        if value is None:
            return value

        return json.loads(value)

    # pylint: disable=unused-argument
    def to_python(self, value):
        """
        Convert JSON String to object
        """
        if value is None or isinstance(value, JSONField):
            return value

        return json.loads(value)

    # pylint: disable=unused-argument
    def get_prep_value(self, value):
        """
        Convert back to text
        """
        return json.dumps(value)
