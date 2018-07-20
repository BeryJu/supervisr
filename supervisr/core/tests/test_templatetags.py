"""
Supervisr Core Templatetags Test
"""

from django.template import Context
from django.test import TestCase
from supervisr.core.utils import render_from_string


class TestTemplateTagss(TestCase):
    """
    Supervisr Core Templatetags Test
    """

    def test_ifapp_tag(self):
        """Test ifapp tag"""
        self.assertEqual('False',
                         render_from_string("{% load ifapp %}{% ifapp 'test' %}", ctx=Context()))

    # def test_supervisr_dyn_modlist(self):
    #     """Test supervisr_dyn_modlist tag"""
    #     self.assertEqual('False', render_from_string(
    #         "{% load supervisr_dyn_modlist %}{% supervisr_dyn_modlist %}", ctx=Context()))
