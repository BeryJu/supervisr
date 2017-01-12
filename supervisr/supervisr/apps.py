from __future__ import unicode_literals
import os
from django.apps import AppConfig
from django.conf import settings

class SupervisrCoreConfig(AppConfig):
    name = 'supervisr'

    def ready(self):
        dir = os.path.dirname(__file__)
        two_up = os.path.split(os.path.split(dir)[0])[0]
        changelog_file = os.path.join(two_up, 'CHANGELOG.md')
        try:
            f = open(changelog_file, 'r')
            settings.CHANGELOG = f.read()
            f.close()
        except Exception as e:
            settings.CHANGELOG = 'Failed to load Changelog.md'
