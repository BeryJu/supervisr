"""
Supervisr Server Config tests
"""

import os
import unittest

from django.apps import apps


def get_tests(app):
    """
    Get server tests from app
    e.g.
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(get_tests('mail'))
    """
    app_config = apps.get_app_config(app)
    dir = os.path.join(os.path.dirname(app_config.module.__file__), 'server/tests/')
    loader = unittest.TestLoader()
    tests = loader.discover(dir)
    return tests
