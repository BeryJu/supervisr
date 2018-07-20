"""
Supervisr Core Event Test
"""

from django.test import TestCase
from supervisr.core.models import Event, User


class TestEvent(TestCase):
    """
    Supervisr Core Event Test
    """

    def setUp(self):
        self.user = User.objects.create(
            username="Test User a",
            email="testa@test.test")

    def test_send_notification(self):
        """
        Test Event's send_notification
        """
        Event.objects.create(
            user=self.user,
            message='test',
            send_notification=True)
