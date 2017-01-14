"""
Supervisr Core Markdown Templatettags
"""
import logging

from django import template
from django.utils.safestring import mark_safe
from markdown import markdown as markdown_render

REGISTER = template.Library()

LOGGER = logging.getLogger(__name__)

@REGISTER.tag(name="blockmarkdown")
# pylint: disable=unused-argument
def markdown_tag(parser, token):
    """
    Render markdown between blockmarkdown and endblockmarkdown with MarkdownNode
    """
    nodelist = parser.parse(('endblockmarkdown',))
    parser.delete_first_token() # consume '{% endblockmarkdown %}'
    return MarkdownNode(nodelist)

class MarkdownNode(template.Node):
    """
    Render markdown between blockmarkdown and endblockmarkdown
    """

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        Render markdown between blockmarkdown and endblockmarkdown
        """
        value = self.nodelist.render(context)
        return mark_safe(markdown_render(value))

@REGISTER.simple_tag
def markdown(mdwn):
    """
    Simple tag to render markdown from a variable
    """
    return mark_safe(markdown_render(mdwn))
