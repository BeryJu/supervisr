"""
Supervisr Core Middleware to add a banner message
"""

from django.contrib import messages

from supervisr.core.models import Setting
from supervisr.core.utils import messages_add_once


def permanent_message(get_response):
    """Middleware Permanently add a message"""

    def middleware(req):
        """Middleware Permanently add a message"""
        m_enabled = Setting.get_bool('banner:enabled')
        m_text = Setting.get('banner:message')
        m_level = Setting.get('banner:level')

        if m_enabled is True and req.user.is_authenticated:
            messages_add_once(req, getattr(messages, m_level.upper()), m_text)
        return get_response(req)

    return middleware
