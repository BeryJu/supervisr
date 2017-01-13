from __future__ import unicode_literals

import os
import subprocess

from django.apps import AppConfig
from django.conf import settings


class SupervisrCoreConfig(AppConfig):
    name = 'supervisr'

    def ready(self):
        # Looks ugly, but just goes two dirs up and gets CHANGELOG.md
        dir = os.path.dirname(__file__)
        two_up = os.path.split(os.path.split(dir)[0])[0]
        changelog_file = os.path.join(two_up, 'CHANGELOG.md')
        try:
            f = open(changelog_file, 'r')
            settings.CHANGELOG = f.read()
            f.close()
        except Exception as e:
            settings.CHANGELOG = 'Failed to load Changelog.md'
        # Read this commit's shortened hash if git is in the path
        try:
            hash = subprocess.Popen(['git', 'log', '--pretty=format:%h', '-n 1'],
                stdout=subprocess.PIPE).communicate()[0]
            settings.VERSION_HASH = hash
        except Exception as e:
            settings.VERSION_HASH = 'dev'
