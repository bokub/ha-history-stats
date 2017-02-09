"""
Component to make instant statistics about your history.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.history_stats/
"""

import datetime
import logging
import math

import voluptuous as vol

import homeassistant.components.history as history
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_ENTITY_ID, CONF_STATE, EVENT_HOMEASSISTANT_START)
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_state_change

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'history_stats'
DEPENDENCIES = ['history']

CONF_START = 'start'
CONF_END = 'end'
CONF_DURATION = 'duration'
CONF_PERIOD_KEYS = [CONF_START, CONF_END, CONF_DURATION]

DEFAULT_NAME = 'unnamed statistics'
UNIT = 'h'
UNIT_RATIO = '%'
ICON = 'mdi:chart-line'

ATTR_START = 'from'
ATTR_END = 'to'
ATTR_VALUE = 'value'
ATTR_RATIO = 'ratio'


def exactly_two_period_keys(conf):
    """Ensure exactly 2 of CONF_PERIOD_KEYS are provided."""
    provided = 0

    for param in CONF_PERIOD_KEYS:
        if param in conf and conf[param] is not None:
            provided += 1

    if provided != 2:
        raise vol.Invalid('You must provide exactly 2 of the following:'
                          ' start, end, duration')
    return conf


PLATFORM_SCHEMA = vol.All(PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITY_ID): cv.entity_id,
    vol.Required(CONF_STATE): cv.slug,
    vol.Optional(CONF_START, default=None): cv.template,
    vol.Optional(CONF_END, default=None): cv.template,
    vol.Optional(CONF_DURATION, default=None): cv.time_period,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
}), exactly_two_period_keys)


# noinspection PyUnusedLocal
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the History Stats sensor."""
    entity_id = config.get(CONF_ENTITY_ID)
    entity_state = config.get(CONF_STATE)
    start = config.get(CONF_START)
    end = config.get(CONF_END)
    duration = config.get(CONF_DURATION)
    name = config.get(CONF_NAME)

    for template in [start, end]:
        if template is not None:
            template.hass = hass

    add_devices([HistoryStatsSensor(
        hass, entity_id, entity_state, start, end, duration, name)])

    return True


class HistoryStatsSensor(Entity):
    """Representation of a HistoryStats sensor."""

    def __init__(
            self, hass, entity_id, entity_state, start, end, duration, name):
        """Initialize the HistoryStats sensor."""
        self._hass = hass

        self._entity_id = entity_id
        self._entity_state = entity_state
        self._duration = duration
        self._start = start
        self._end = end
        self._name = name
        self._unit_of_measurement = UNIT

        self._period = (datetime.datetime.now(), datetime.datetime.now())
        self.value = 0

        def force_refresh(*args):
            """Force the component to refresh."""
            self.schedule_update_ha_state(True)

        # Update value when home assistant starts
        hass.bus.listen_once(EVENT_HOMEASSISTANT_START, force_refresh)

        # Update value when tracked entity changes its state
        track_state_change(hass, entity_id, force_refresh)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return round(self.value, 2)

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def should_poll(self):
        """Polling required."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        start, end = self._period
        hsh = HistoryStatsHelper
        return {
            ATTR_VALUE: hsh.pretty_duration(self.value),
            ATTR_RATIO: hsh.pretty_ratio(self.value, self._period),
            ATTR_START: start.strftime('%Y-%m-%d %H:%M:%S'),
            ATTR_END: end.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Get the latest data and updates the states."""
        # Parse templates
        self.update_period()
        start, end = self._period

        # Convert to UTC
        start = dt_util.as_utc(start)
        end = dt_util.as_utc(end)

        # Get history between start and end
        history_list = history.state_changes_during_period(
            start, end, str(self._entity_id))

        if self._entity_id not in history_list.keys():
            return

        # Get the first state
        last_state = history.get_state(start, self._entity_id)
        last_state = (last_state is not None and
                      last_state == self._entity_state)
        last_time = dt_util.as_timestamp(start)
        elapsed = 0

        # Make calculations
        for item in history_list.get(self._entity_id):
            current_state = item.state == self._entity_state
            current_time = item.last_changed.timestamp()

            if last_state:
                elapsed += current_time - last_time

            last_state = current_state
            last_time = current_time

        # Save value in hours
        self.value = elapsed / 3600

    def update_period(self):
        """Parse the templates and store a datetime tuple in _period."""
        start = None
        end = None

        # Parse start
        if self._start is not None:
            try:
                start_rendered = self._start.render()
            except TemplateError as ex:
                HistoryStatsHelper.handle_template_exception(ex, 'start')
                return
            start = dt_util.parse_datetime(start_rendered)
            if start is None:
                try:
                    start = dt_util.as_local(dt_util.utc_from_timestamp(
                        math.floor(float(start_rendered))))
                except ValueError:
                    _LOGGER.error('PARSING ERROR: start must be a datetime'
                                  ' or a timestamp.')
                    return

        # Parse end
        if self._end is not None:
            try:
                end_rendered = self._end.render()
            except TemplateError as ex:
                HistoryStatsHelper.handle_template_exception(ex, 'end')
                return
            end = dt_util.parse_datetime(end_rendered)
            if end is None:
                try:
                    end = dt_util.as_local(dt_util.utc_from_timestamp(
                        math.floor(float(end_rendered))))
                except ValueError:
                    _LOGGER.error('PARSING ERROR: end must be a datetime'
                                  ' or a timestamp.')
                    return

        # Calculate start or end using the duration
        if start is None:
            start = end - self._duration
        if end is None:
            end = start + self._duration

        self._period = start, end


class HistoryStatsHelper:
    """Static methods to make the HistoryStatsSensor code lighter."""

    @staticmethod
    def pretty_duration(hours):
        """Format a duration in days, hours, minutes, seconds."""
        seconds = int(3600 * hours)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '%dd %dh %dm %ds' % (days, hours, minutes, seconds)
        elif hours > 0:
            return '%dh %dm %ds' % (hours, minutes, seconds)
        elif minutes > 0:
            return '%dm %ds' % (minutes, seconds)
        else:
            return '%ds' % (seconds,)

    @staticmethod
    def pretty_ratio(value, period):
        """Format the ratio of value / period duration."""
        if len(period) != 2 or period[0] == period[1]:
            return '0,0' + UNIT_RATIO

        ratio = 100 * 3600 * value / (period[1] - period[0]).total_seconds()
        return str(round(ratio, 1)) + UNIT_RATIO

    @staticmethod
    def handle_template_exception(ex, field):
        """Log an error nicely if the template cannot be interpreted."""
        if ex.args and ex.args[0].startswith(
                "UndefinedError: 'None' has no attribute"):
            # Common during HA startup - so just a warning
            _LOGGER.warning(ex)
            return
        _LOGGER.error('Error parsing template for [' + field + ']')
        _LOGGER.error(ex)
