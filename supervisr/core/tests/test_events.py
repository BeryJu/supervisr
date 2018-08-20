"""Supervisr Core Event Test"""

from supervisr.core.models import Event
from supervisr.core.tests.utils import TestCase


class TestEvent(TestCase):
    """Supervisr Core Event Test"""

    def test_send_notification(self):
        """Test Event's send_notification"""
        Event.objects.create(
            user=self.system_user,
            message='test',
            send_notification=True)
