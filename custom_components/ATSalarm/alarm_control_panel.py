"""Interfaces with ATS alarm control panels."""
import logging
import re

from ATSAPI import ATSalarm
import voluptuous as vol

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.components.alarm_control_panel import PLATFORM_SCHEMA
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.const import (
    CONF_NAME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
)

import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_alarmIP = 'alarmIP'
CONF_alarmPort = 'alarmPort'
CONF_alarmCode = 'alarmCode'
CONF_alarmPin = 'alarmPin'

DEFAULT_NAME = "ATS.alarm"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_alarmIP): cv.string,
        vol.Required(CONF_alarmPort): cv.string,
        vol.Required(CONF_alarmCode): cv.string,
        vol.Required(CONF_alarmPin): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up a ATS-alarm control panel."""
    alarmIP = config.get(CONF_alarmIP)
    alarmPort = config.get(CONF_alarmPort)
    alarmCode = config.get(CONF_alarmCode)
    alarmPin = config.get(CONF_alarmPin)
    name = "ATS alarm"

    _LOGGER.error("this is the alarmPin : " + alarmPin)

    atsalarm = ATSalarm(hass=hass, name=name, alarmIP=alarmIP, alarmPort=alarmPort, alarmCode=alarmCode, alarmPin=alarmPin)
    async_add_entities([atsalarm])

    return true


class ATSalarm(alarm.AlarmControlPanel):
    """Representation of an ATS alarm status."""

    def __init__(self, hass, name, alarmIP, alarmPort, alarmCode, alarmPin):
        """Initialize the ATS alarm status."""

        _LOGGER.debug("Setting up ATS alarm...")
        self._hass = hass
        self._name = name
        self._alarmIP = alarmIP
        self._alarmPort = alarmPort
        self._alarmCode = alarmCode
        self._alarmPin = alarmPin
        self._state = None
        self._alarm = ATSalarm(alarmIP=alarmIP, alarmPort=alarmPort, alarmCode=alarmCode, alarmPin=alarmPin, hass.loop)

    async def async_update(self):
        """Fetch the latest state."""
        await self._alarm.async_update()
        return self._alarm.state

    @property
    def name(self):
        """Return the name of the alarm."""
        return self._name


    @property
    def state(self):
        """Return the state of the device."""
        if self._alarm.state.lower() == "disarmed":
            return STATE_ALARM_DISARMED
        if self._alarm.state.lower() == "armed away":
            return STATE_ALARM_ARMED_AWAY
        return None

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_AWAY

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {"sensor_status": self._alarm.sensor_status}

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        if self._validate_code(code):
            await self._alarm.async_alarm_disarm()

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        if self._validate_code(code):
            await self._alarm.async_alarm_arm_home()

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        if self._validate_code(code):
            await self._alarm.async_alarm_arm_away()


