"""
Supervisr Mail Domains Templatetag
"""
from django import template

from supervisr.mail.models import MailDomain

register = template.Library()

@register.simple_tag(takes_context=True)
def mail_domains(context):
    """
    Return list of domains for current user
    """
    if 'request' in context:
        return MailDomain.objects \
            .filter(users__in=[context['request'].user]) \
            .order_by('domain__domain')
    return []
