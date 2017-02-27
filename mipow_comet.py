"""
Support for mipow comet led stripes.
For more details about this platform, please refer to the documentation at
https://github.com/papagei9/hass-mipow-comet
"""
import logging

import voluptuous as vol

from homeassistant.const import CONF_DEVICES, CONF_NAME
from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_WHITE_VALUE, ATTR_BRIGHTNESS,
    SUPPORT_RGB_COLOR, SUPPORT_WHITE_VALUE, SUPPORT_BRIGHTNESS, SUPPORT_EFFECT, SUPPORT_FLASH, EFFECT_COLORLOOP, EFFECT_RANDOM, Light, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv

# REQUIREMENTS = ['python-mipow==0.3']

_LOGGER = logging.getLogger(__name__)

SUPPORT_MIPOW_COMET = (SUPPORT_RGB_COLOR | SUPPORT_WHITE_VALUE | SUPPORT_BRIGHTNESS | SUPPORT_EFFECT | SUPPORT_FLASH)


DEVICE_SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA},
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the mipow COMET platform."""
    lights = []
    for address, device_config in config[CONF_DEVICES].items():
        device = {}
        device['name'] = device_config[CONF_NAME]
        device['address'] = address
        light = mipowComet(device)
        if light.is_valid:
            lights.append(light)

    add_devices(lights)


class mipowComet(Light):
    """Representation of a mipow COMET."""

    def __init__(self, device):
        """Initialize the light."""
        import mipow_comet

        self._name = device['name']
        self._address = device['address']
        self.is_valid = True
        self._bulb = mipow_comet.mipow_comet(self._address)
        self._white = 0
        self._rgb = (0, 0, 0)
        self._state = False
        self._brightness = 255
        if self._bulb.connect() is False:
            self.is_valid = False
            _LOGGER.error(
                "Failed to connect to bulb %s, %s", self._address, self._name)
            return
        self.update()

    @property
    def unique_id(self):
        """Return the ID of this light."""
        return "{}.{}".format(self.__class__, self._address)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def rgb_color(self):
        """Return the color property."""
        return self._rgb

    @property
    def white_value(self):
        """Return the white property."""
        return self._white

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_MIPOW_COMET

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return [EFFECT_COLORLOOP, EFFECT_RANDOM]

    @property
    def should_poll(self):
        """Feel free to poll."""
        return True

    @property
    def assumed_state(self):
        """We can report the actual state."""
        return False

    @property
    def brightness(self):
        """Return the brightness."""
        return self._brightness

    def set_rgb(self, red, green, blue):
        """Set the rgb state."""
        # self.connect()
        result = self._bulb.set_rgb(red, green, blue)
        """return"""
        # self.disconnect()
        return result

    def set_white(self, white):
        """Set the white state."""
        # self.connect()
        result = self._bulb.set_white(white)
        """return"""
        # self.disconnect()
        return result

    def set_brighntess(self, brightness):
        """Set the brightness."""
        result = self._bulb.set_brightness(brightness)
        return result

    def turn_on(self, **kwargs):
        """Turn the specified light on."""
        # self.connect()
        self._state = True
        self._bulb.on()

        rgb = kwargs.get(ATTR_RGB_COLOR)
        white = kwargs.get(ATTR_WHITE_VALUE)
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        self._brightness = brightness

        if white is not None:
            self._white = white
            self._rgb = (0, 0, 0)

        if rgb is not None:
            self._white = 0
            self._rgb = rgb

        if self._white != 0:
            self.set_white(self._white)
        else:
            self.set_rgb(self._rgb[0], self._rgb[1], self._rgb[2])

        self.set_brightness(self._brightness)
        # self.disconnect()

    def turn_off(self, **kwargs):
        """Turn the specified light off."""
        # self.connect()
        self._state = False
        return self._bulb.off()
        # self.disconnect()

    def update(self):
        """Synchronise internal state with the actual light state."""
        # self.connect()
        self._rgb = self._bulb.get_colour()
        self._white = self._bulb.get_white()
        self._state = self._bulb.get_on()
        self._brightness = self._bulb.get_brightness()
        # self.disconnect()

    def update_init(self):
        """Update without connect"""
        self._rgb = self._bulb.get_colour()
        self._white = self._bulb.get_white()
        self._state = self._bulb.get_on()
        self._brightness = self._bulb.get_brightness()
        # self.disconnect()

    def connect(self):
        if self._bulb.connect() is False:
            self.is_valid = False
            _LOGGER.error(
                "Failed to connect to bulb %s, %s", self._address, self._name)
            return

    def disconnect(self):
        return self._bulb.disconnect()
