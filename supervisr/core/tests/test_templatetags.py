"""Supervisr Core Templatetags Test"""

from django.template import Context
from django.test import TestCase

from supervisr.core.utils import render_from_string


class TestTemplateTagss(TestCase):
    """Supervisr Core Templatetags Test"""

    def test_ifapp_tag(self):
        """Test ifapp tag"""
        self.assertEqual('False',
                         render_from_string("{% load supervisr_ifapp %}{% ifapp 'test' %}",
                                            ctx=Context()))
