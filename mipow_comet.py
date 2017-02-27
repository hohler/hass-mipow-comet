"""
Support for mipow comet led stripes.
For more details about this platform, please refer to the documentation at
https://github.com/papagei9/hass-mipow-comet
"""
import logging
import random

import voluptuous as vol

from homeassistant.const import CONF_DEVICES, CONF_NAME
from homeassistant.components.light import (
    ATTR_RGB_COLOR, ATTR_WHITE_VALUE, ATTR_BRIGHTNESS, ATTR_EFFECT,
    SUPPORT_RGB_COLOR, SUPPORT_WHITE_VALUE, SUPPORT_BRIGHTNESS, SUPPORT_EFFECT, EFFECT_COLORLOOP, EFFECT_RANDOM, Light, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv

# REQUIREMENTS = ['python-mipow==0.3']

_LOGGER = logging.getLogger(__name__)

SUPPORT_MIPOW_COMET = (SUPPORT_RGB_COLOR | SUPPORT_WHITE_VALUE | SUPPORT_BRIGHTNESS | SUPPORT_EFFECT)


DEVICE_SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA},
})

# List of support effects which aren't already declared
EFFECT_CANDLE = 'color_candle'
EFFECT_FADE = 'color_fade'
EFFECT_COLORJUMP = 'color_jump'
EFFECT_BLINK = 'color_blink'

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
        return [EFFECT_RANDOM, EFFECT_BLINK, EFFECT_COLORLOOP, EFFECT_COLORJUMP, EFFECT_FADE, EFFECT_CANDLE]

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

    def set_brightness(self, brightness):
        """Set the brightness."""
        result = self._bulb.set_brightness(brightness)
        return result

# (self, red, green, blue, mode, speed):
    def set_effect(self, effect):
        if effect == EFFECT_RANDOM:
            self.set_rgb(random.randrange(0, 255), random.randrange(0, 255), random.randrange(255))
        elif effect == EFFECT_COLORLOOP:
            self._bulb.set_effect(self._rgb[0], self._rgb[1], self._rgb[2], 0x03, 0x14)
        elif effect == EFFECT_COLORJUMP:
            self._bulb.set_effect(0x00, 0x00, 0x00, 0x02, 0x14)
        elif effect == EFFECT_CANDLE:
            self._bulb.set_effect(self._rgb[0], self._rgb[1], self._rgb[2], 0x04, 0x14)
        elif effect == EFFECT_BLINK:
            self._bulb.set_effect(self._rgb[0], self._rgb[1], self._rgb[2], 0x00, 0x14)
        elif effect == EFFECT_FADE:
            self._bulb.set_effect(self._rgb[0], self._rgb[1], self._rgb[2], 0x01, 0x14)

    def turn_on(self, **kwargs):
        """Turn the specified light on."""
        # self.connect()
        self._state = True
        self._bulb.on()

        rgb = kwargs.get(ATTR_RGB_COLOR)
        white = kwargs.get(ATTR_WHITE_VALUE)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)

        self._brightness = brightness

        if white is not None:
            self._white = white
            self._rgb = (0, 0, 0)

        if rgb is not None:
            self._white = 0
            self._rgb = rgb

        if self._white != 0:
            self.set_white(self._white)
        elif self._rgb != (0, 0, 0) and effect is None:
            self.set_rgb(self._rgb[0], self._rgb[1], self._rgb[2])
            if brightness is not None:
                self.set_brightness(self._brightness)
        elif effect is not None:
            self._effect = effect
            self.set_effect(effect)
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
