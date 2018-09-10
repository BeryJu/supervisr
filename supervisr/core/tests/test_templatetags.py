"""Supervisr Core Templatetags Test"""

from django.template import Context

from supervisr.core.utils import render_from_string
from supervisr.core.utils.tests import TestCase


class TestTemplateTags(TestCase):
    """Supervisr Core Templatetags Test"""

    def test_ifapp_tag(self):
        """Test ifapp tag"""
        self.assertEqual('False',
                         render_from_string("{% load supervisr_ifapp %}{% ifapp 'test' %}",
                                            ctx=Context()))
