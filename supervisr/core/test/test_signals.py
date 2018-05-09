"""Supervisr Core Signals Test"""

from supervisr.core.signals import RobustSignal, SignalException
from supervisr.core.test.utils import TestCase


class TestSignals(TestCase):
    """Supervisr Core Signals Test"""

    def setUp(self):
        super(TestSignals, self).setUp()
        self.sig_test = RobustSignal()  # This signal is only used during unit-tests

    def test_robust_signal(self):
        """Test RobustSignal's error catching"""
        self.sig_test.disconnect()

        # pylint: disable=unused-argument
        def handler(*args, **kwargs):
            """
            Throw an exception
            """
            return 0 / 0

        self.sig_test.connect(handler)
        try:
            self.sig_test.send(sender=None)
        except SignalException as exc:
            self.assertTrue(isinstance(exc, SignalException))
