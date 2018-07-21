"""supervisr mod stats influx task tests"""

from supervisr.core.models import Setting
from supervisr.core.tests.utils import TestCase
from supervisr.mod.stats.influx.tasks import push_influx_data


class TestTasks(TestCase):
    """Test tasks"""

    def setUp(self):
        super(TestTasks, self).setUp()
        Setting.set('enabled', True)

    def test_push_influx_data(self):
        """Test Push task"""
        push_influx_data.delay()
