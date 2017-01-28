"""The test for the History Statistics sensor platform."""
import unittest

from homeassistant.bootstrap import setup_component
from tests.common import get_test_home_assistant


class TestHistoryStatsSensor(unittest.TestCase):
    """Test the History Statistics sensor."""

    def setUp(self):
        """Set up things to be run when tests are started."""
        self.hass = get_test_home_assistant()

        config = {
            'sensor': {
                'platform': 'history_stats',
                'entity_id': 'binary_sensor.test_id',
                'state': 'on',
                'start': '\'{{ _TODAY_ }}\'',
                'end': '\'{{ _NOW_ }}\'',
            }
        }

        self.assertTrue(setup_component(self.hass, 'sensor', config))

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()
