"""The test for the History Statistics sensor platform."""
# pylint: disable=protected-access
from datetime import timedelta
import unittest
from unittest.mock import patch

from homeassistant.const import STATE_UNKNOWN
from homeassistant.setup import setup_component
from homeassistant.components.sensor.history_stats import HistoryStatsSensor
import homeassistant.core as ha
from homeassistant.helpers.template import Template
import homeassistant.util.dt as dt_util

from tests.common import init_recorder_component, get_test_home_assistant


class TestHistoryStatsSensor(unittest.TestCase):
    """Test the History Statistics sensor."""

    def setUp(self):
        """Set up things to be run when tests are started."""
        self.hass = get_test_home_assistant()

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()

    def test_setup(self):
        """Test the history statistics sensor setup."""
        self.init_recorder()
        config = {
            'history': {
            },
            'sensor': {
                'platform': 'history_stats',
                'entity_id': 'binary_sensor.test_id',
                'state': 'on',
                'start': '{{ now().replace(hour=0)'
                         '.replace(minute=0).replace(second=0) }}',
                'duration': '02:00',
                'name': 'Test',
            }
        }

        self.assertTrue(setup_component(self.hass, 'sensor', config))

        state = self.hass.states.get('sensor.test')
        self.assertEqual(state.state, STATE_UNKNOWN)

    def test_period_parsing(self):
        """Test the conversion from templates to period."""
        today = Template('{{ now().replace(hour=0).replace(minute=0)'
                         '.replace(second=0) }}', self.hass)
        duration = timedelta(hours=2, minutes=1)

        sensor1 = HistoryStatsSensor(
            self.hass, 'test', 'on', today, None, duration, 'time', 'test')
        sensor2 = HistoryStatsSensor(
            self.hass, 'test', 'on', None, today, duration, 'time', 'test')

        sensor1.update_period()
        sensor1_start, sensor1_end = sensor1._period
        sensor2.update_period()
        sensor2_start, sensor2_end = sensor2._period

        # Start = 00:00:00
        self.assertEqual(sensor1_start.hour, 0)
        self.assertEqual(sensor1_start.minute, 0)
        self.assertEqual(sensor1_start.second, 0)

        # End = 02:01:00
        self.assertEqual(sensor1_end.hour, 2)
        self.assertEqual(sensor1_end.minute, 1)
        self.assertEqual(sensor1_end.second, 0)

        # Start = 21:59:00
        self.assertEqual(sensor2_start.hour, 21)
        self.assertEqual(sensor2_start.minute, 59)
        self.assertEqual(sensor2_start.second, 0)

        # End = 00:00:00
        self.assertEqual(sensor2_end.hour, 0)
        self.assertEqual(sensor2_end.minute, 0)
        self.assertEqual(sensor2_end.second, 0)

    def test_measure(self):
        """Test the history statistics sensor measure."""
        t0 = dt_util.utcnow() - timedelta(minutes=40)
        t1 = t0 + timedelta(minutes=20)
        t2 = dt_util.utcnow() - timedelta(minutes=10)

        # Start     t0        t1        t2        End
        # |--20min--|--20min--|--10min--|--10min--|
        # |---off---|---on----|---off---|---on----|

        fake_states = {
            'binary_sensor.test_id': [
                ha.State('binary_sensor.test_id', 'on', last_changed=t0),
                ha.State('binary_sensor.test_id', 'off', last_changed=t1),
                ha.State('binary_sensor.test_id', 'on', last_changed=t2),
            ]
        }

        start = Template('{{ as_timestamp(now()) - 3600 }}', self.hass)
        end = Template('{{ now() }}', self.hass)

        sensor1 = HistoryStatsSensor(
            self.hass, 'binary_sensor.test_id', 'on', start, end, None,
            'time', 'Test')

        sensor2 = HistoryStatsSensor(
            self.hass, 'unknown.id', 'on', start, end, None, 'time', 'Test')

        sensor3 = HistoryStatsSensor(
            self.hass, 'binary_sensor.test_id', 'on', start, end, None,
            'count', 'test')

        sensor4 = HistoryStatsSensor(
            self.hass, 'binary_sensor.test_id', 'on', start, end, None,
            'ratio', 'test')

        self.assertEqual(sensor1._type, 'time')
        self.assertEqual(sensor3._type, 'count')
        self.assertEqual(sensor4._type, 'ratio')

        with patch('homeassistant.components.history.'
                   'state_changes_during_period', return_value=fake_states):
            with patch('homeassistant.components.history.get_state',
                       return_value=None):
                sensor1.update()
                sensor2.update()
                sensor3.update()
                sensor4.update()

        self.assertEqual(sensor1.state, 0.5)
        self.assertEqual(sensor2.state, None)
        self.assertEqual(sensor3.state, 2)
        self.assertEqual(sensor4.state, 50)

    def test_wrong_date(self):
        """Test when start or end value is not a timestamp or a date."""
        good = Template('{{ now() }}', self.hass)
        bad = Template('{{ TEST }}', self.hass)

        sensor1 = HistoryStatsSensor(
            self.hass, 'test', 'on', good, bad, None, 'time', 'Test')
        sensor2 = HistoryStatsSensor(
            self.hass, 'test', 'on', bad, good, None, 'time', 'Test')

        before_update1 = sensor1._period
        before_update2 = sensor2._period

        sensor1.update_period()
        sensor2.update_period()

        self.assertEqual(before_update1, sensor1._period)
        self.assertEqual(before_update2, sensor2._period)

    def test_wrong_duration(self):
        """Test when duration value is not a timedelta."""
        self.init_recorder()
        config = {
            'history': {
            },
            'sensor': {
                'platform': 'history_stats',
                'entity_id': 'binary_sensor.test_id',
                'name': 'Test',
                'state': 'on',
                'start': '{{ now() }}',
                'duration': 'TEST',
            }
        }

        setup_component(self.hass, 'sensor', config)
        self.assertEqual(self.hass.states.get('sensor.test'), None)
        self.assertRaises(TypeError,
                          setup_component(self.hass, 'sensor', config))

    def test_bad_template(self):
        """Test Exception when the template cannot be parsed."""
        bad = Template('{{ x - 12 }}', self.hass)  # x is undefined
        duration = '01:00'

        sensor1 = HistoryStatsSensor(
            self.hass, 'test', 'on', bad, None, duration, 'time', 'Test')
        sensor2 = HistoryStatsSensor(
            self.hass, 'test', 'on', None, bad, duration, 'time', 'Test')

        before_update1 = sensor1._period
        before_update2 = sensor2._period

        sensor1.update_period()
        sensor2.update_period()

        self.assertEqual(before_update1, sensor1._period)
        self.assertEqual(before_update2, sensor2._period)

    def test_not_enough_arguments(self):
        """Test config when not enough arguments provided."""
        self.init_recorder()
        config = {
            'history': {
            },
            'sensor': {
                'platform': 'history_stats',
                'entity_id': 'binary_sensor.test_id',
                'name': 'Test',
                'state': 'on',
                'start': '{{ now() }}',
            }
        }

        setup_component(self.hass, 'sensor', config)
        self.assertEqual(self.hass.states.get('sensor.test'), None)
        self.assertRaises(TypeError,
                          setup_component(self.hass, 'sensor', config))

    def test_too_many_arguments(self):
        """Test config when too many arguments provided."""
        self.init_recorder()
        config = {
            'history': {
            },
            'sensor': {
                'platform': 'history_stats',
                'entity_id': 'binary_sensor.test_id',
                'name': 'Test',
                'state': 'on',
                'start': '{{ as_timestamp(now()) - 3600 }}',
                'end': '{{ now() }}',
                'duration': '01:00',
            }
        }

        setup_component(self.hass, 'sensor', config)
        self.assertEqual(self.hass.states.get('sensor.test'), None)
        self.assertRaises(TypeError,
                          setup_component(self.hass, 'sensor', config))

    def init_recorder(self):
        """Initialize the recorder."""
        init_recorder_component(self.hass)
        self.hass.start()
