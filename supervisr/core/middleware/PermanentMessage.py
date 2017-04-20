"""
Supervisr Core Middleware to add a banner message
"""

from django.contrib import messages

from ..models import Setting


def permanent_message(get_response):
    """
    Middleware Permenently add a message
    """
    m_enabled = Setting.objects.get(
        key='supervisr:banner:enabled').value_bool
    m_text = Setting.objects.get(
        key='supervisr:banner:message').value
    m_level = Setting.objects.get(
        key='supervisr:banner:level').value

    def middleware(req):
        """
        Middleware Permenently add a message
        """
        if m_enabled is True:
            # Get existing Messages and only add if we're not in there
            storage = messages.get_messages(req)
            m_exists = False
            for message in storage:
                if message.message == m_text:
                    m_exists = True
            storage.used = False
            if not m_exists:
                messages.add_message(req, getattr(messages, m_level.upper()), m_text)
        response = get_response(req)
        return response
    return middleware
