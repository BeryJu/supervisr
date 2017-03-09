"""
Supervisr Core Google Analytics Templatetag
"""

from django import template
from django.utils.safestring import mark_safe

from ..models import Setting

register = template.Library()

@register.simple_tag(takes_context=True)
def google_analytics(context, tracking_id=''):
    """
    Returns the GA Script with tracking_id inserted
    """
    if Setting.objects.get(pk='supervisr:analytics:ga:enabled').value_bool is False:
        # Google Analytics is not enabled
        return ''
    if tracking_id is '':
        tracking_id = Setting.get('supervisr:analytics:ga:tracking_id')
    if tracking_id is None or tracking_id is False:
        # Check if tracking is disabled
        return ''
    # Check if we're signed in and pass the user through
    req = context['request']
    if req.user.is_authenticated:
        user_id = req.user.pk
    else:
        user_id = 'Anonymous'
    return mark_safe("""
    <script>
    window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;
    ga('create', '%(tracking_id)s', 'auto', {
      userId: '%(user_id)s',
    });
    ga('send', 'pageview');
    </script>
    <script async src='https://www.google-analytics.com/analytics.js'></script>
    """ % {
        'tracking_id': tracking_id,
        'user_id': user_id
    })
