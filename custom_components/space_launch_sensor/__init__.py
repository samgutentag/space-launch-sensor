"""The Space Launch Sensor integration."""

from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List of platforms (sensor, binary_sensor, etc.) that this integration supports
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Space Launch Sensor integration from YAML configuration."""
    # This function handles YAML-based setup
    # Since we're keeping YAML support (no config flow yet), we need this

    # Initialize domain data storage
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Space Launch Sensor integration setup from YAML")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Space Launch Sensor from a config entry."""
    # This function would handle UI-based setup (config flow)
    # We'll implement this later when we add config flow support

    _LOGGER.debug("Setting up Space Launch Sensor config entry: %s", entry.entry_id)

    # Store configuration data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Set up platforms (in our case, just sensors)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Clean up when the integration is removed
    _LOGGER.debug("Unloading Space Launch Sensor config entry: %s", entry.entry_id)

    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove configuration data
        hass.data[DOMAIN].pop(entry.entry_id)

        # If this was the last config entry, clean up the domain data
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
