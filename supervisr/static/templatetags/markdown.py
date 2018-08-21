"""supervisr Static Markdown Templatettags"""
import logging

from django import template
from django.utils.safestring import mark_safe
from markdown import markdown as markdown_render

register = template.Library()

LOGGER = logging.getLogger(__name__)


@register.simple_tag
def markdown(source):
    """Simple tag to render markdown from a variable"""
    # markdown_render returns HTML so we have to mark_safe
    return mark_safe(markdown_render(source, extensions=['markdown.extensions.tables'])) # nosec
