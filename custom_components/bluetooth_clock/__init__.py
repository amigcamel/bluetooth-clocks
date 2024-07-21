"""Custom component exposing a service to set Bluetooth clock."""
from __future__ import annotations

import logging
import subprocess

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

DOMAIN = "bluetooth_clock"
_LOGGER = logging.getLogger(__name__)

CONF_MAC_ADDRESS = "mac_address"
CONF_TARGET =  "target"
CONF_TIME = "time"

SET_CLOCK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC_ADDRESS): cv.string,
        vol.Required(CONF_TARGET): cv.string,
        vol.Optional(CONF_TIME): cv.string,
    }
)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Bluetooth Clock component."""
    @callback
    def set_bluetooth_clock(call: ServiceCall) -> None:
        """Service to set the Bluetooth clock."""
        mac_address = call.data[CONF_MAC_ADDRESS]
        target = call.data[CONF_TARGET]
        time = call.data.get(CONF_TIME)

        _LOGGER.info(f"Setting Bluetooth clock for {mac_address} to {time}")
        try:
            if target == "lywsd02":
                command = ["bluetooth-clocks", "set", "-a", mac_address]
                if time:
                    command.extend(["-t", time])
            elif target == "CGD1":
                command = ["bluetooth-clocks", "set", "-a", mac_address, "--cgd1"]
            else:
                raise ValueError(f"Unsupported target: {target}")
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            _LOGGER.info(f"Bluetooth clock set successfully: {result.stdout}")
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to set Bluetooth clock: {e.stderr}")

    # Register the service with Home Assistant
    hass.services.async_register(DOMAIN, 'set_clock', set_bluetooth_clock, schema=SET_CLOCK_SCHEMA)

    # Return boolean to indicate that initialization was successfully.
    return True
