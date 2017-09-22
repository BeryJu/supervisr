"""
Supervisr Core Google Analytics Templatetag
"""

from django import template
from django.utils.safestring import mark_safe

from ..models import Setting

register = template.Library()

@register.simple_tag(takes_context=True)
def google_analytics(context):
    """
    Returns the GA Script with tracking_id inserted
    """
    if Setting.get('analytics:ga:enabled') != 'True':
        # Google Analytics is not enabled
        return ''
    tracking_id = Setting.get('analytics:ga:tracking_id')
    # Check if we're signed in and pass the user through
    user_id = 'Anonymous'
    if 'request' in context and 'user' in context['request']:
        req = context['request']
        if req.user.is_authenticated:
            user_id = req.user.pk
    return mark_safe("""
    <script>
    window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;
    ga('create', '%(tracking_id)s', 'auto', {
      userId: '%(user_id)s',
    });
    ga('send', 'pageview');
    </script>
    <script async src='//www.google-analytics.com/analytics.js'></script>
    """ % {
        'tracking_id': tracking_id,
        'user_id': user_id
    })
