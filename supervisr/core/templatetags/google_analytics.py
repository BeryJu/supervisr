"""Supervisr Core Google Analytics Templatetag"""

from django import template
from django.utils.safestring import mark_safe

from supervisr.core.models import Setting

register = template.Library()

SCRIPT_TEMPLATE = """
<script>
window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;
ga('create', '%(tracking_id)s', 'auto', {
userId: '%(user_id)s',
});
ga('send', 'pageview');
</script>
<script async src='//www.google-analytics.com/analytics.js'></script>
"""


@register.simple_tag(takes_context=True)
def google_analytics(context):
    """Returns the GA Script with tracking_id inserted"""
    if not Setting.get_bool('analytics:ga:enabled'):
        # Google Analytics is not enabled
        return ''
    tracking_id = Setting.get('analytics:ga:tracking_id')
    # Check if we're signed in and pass the user through
    user_id = 'Anonymous'
    if 'request' in context:
        req = context.get('request')
        if req.user.is_authenticated:
            user_id = req.user.pk
    return mark_safe(SCRIPT_TEMPLATE % { # nosec
        'tracking_id': tracking_id,
        'user_id': user_id
    })
