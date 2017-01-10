from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
import markdown
register = template.Library()

# Strongly inspired by https://github.com/trentm/django-markdown-deux/blob/master/lib/markdown_deux/templatetags/markdown_deux_tags.py

@register.tag(name="markdown")
def markdown_tag(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    bits = token.split_contents()
    parser.delete_first_token() # consume '{% endmarkdown %}'
    return MarkdownNode(nodelist)

class MarkdownNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        value = self.nodelist.render(context)
        try:
            return mark_safe(markdown.markdown(value))
        except ImportError:
            if settings.DEBUG:
                raise template.TemplateSyntaxError("Error in `markdown` tag: "
                    "The python-markdown2 library isn't installed.")
            return force_text(value)