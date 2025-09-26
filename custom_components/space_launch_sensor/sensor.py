"""Space Launch Sensor platform."""

import logging
from datetime import timedelta
import async_timeout
import aiohttp
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_LAUNCH_LOCATION_ID,
    DEFAULT_NAME,
    DEFAULT_LAUNCH_LOCATION_ID,
    SCAN_INTERVAL,
    API_BASE_URL,
    API_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(
            CONF_LAUNCH_LOCATION_ID, default=DEFAULT_LAUNCH_LOCATION_ID
        ): cv.positive_int,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    }
)


class SpaceLaunchDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Space Launch API."""

    def __init__(
        self, hass: HomeAssistant, launch_location_id: int, scan_interval: timedelta
    ) -> None:
        """Initialize."""
        self.launch_location_id = launch_location_id
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self):
        """Update data via library."""
        # If launch_location_id is 0, get all upcoming launches
        if self.launch_location_id == 0:
            api_url = f"{API_BASE_URL}/launch/upcoming/"
        else:
            api_url = f"{API_BASE_URL}/launch/upcoming/?location__ids={self.launch_location_id}"

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        response.raise_for_status()
                        data = await response.json()

            if "results" in data and data["results"]:
                return data["results"][0]  # Return the next launch
            else:
                raise UpdateFailed("No upcoming launches found")

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Space Launch Tracker sensor based on a config entry."""
    # This is for config flow setup (we'll implement later)
    pass


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the space launch sensor platform."""
    name = config.get(CONF_NAME)
    launch_location_id = config.get(CONF_LAUNCH_LOCATION_ID)
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    # Create coordinator
    coordinator = SpaceLaunchDataUpdateCoordinator(
        hass, launch_location_id, scan_interval
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Add entities
    async_add_entities([SpaceLaunchSensor(coordinator, name)], True)


class SpaceLaunchSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Space Launch Sensor."""

    def __init__(
        self, coordinator: SpaceLaunchDataUpdateCoordinator, name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        # Explicitly set no device class
        self._attr_device_class = None
        self._attr_has_entity_name = True
        # Set state class to None (no numeric state)
        self._attr_state_class = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"space_launch_sensor_{self.coordinator.launch_location_id}_v2"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor (launch name)."""
        if self.coordinator.data:
            return self.coordinator.data.get("name", "Unknown")
        return None

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        return "mdi:rocket"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        launch_data = self.coordinator.data

        # Calculate countdown values
        countdown_attrs = self._calculate_countdown_attributes(launch_data.get("net"))

        # Base attributes from API
        base_attrs = {
            "launch_id": launch_data.get("id"),
            "launch_name": launch_data.get("name"),
            "status": launch_data.get("status", {}).get("name"),
            "net": launch_data.get("net"),
            "window_start": launch_data.get("window_start"),
            "window_end": launch_data.get("window_end"),
            "rocket": launch_data.get("rocket", {})
            .get("configuration", {})
            .get("full_name"),
            "mission": (
                launch_data.get("mission", {}).get("name")
                if launch_data.get("mission")
                else "Unknown"
            ),
            "mission_type": (
                launch_data.get("mission", {}).get("type")
                if launch_data.get("mission")
                else "Unknown"
            ),
            "launch_provider": launch_data.get("launch_service_provider", {}).get(
                "name"
            ),
            "location": launch_data.get("pad", {}).get("location", {}).get("name"),
            "pad": launch_data.get("pad", {}).get("name"),
            "map_url": launch_data.get("pad", {}).get("map_url"),
            "info_url": launch_data.get("url"),
            "image_url": launch_data.get("image"),
        }

        # Merge base attributes with countdown attributes
        return {**base_attrs, **countdown_attrs}

    def _calculate_countdown_attributes(self, net_time: str | None) -> dict:
        """Calculate countdown attributes from launch time."""
        if not net_time:
            return {
                "countdown_days": None,
                "countdown_hours": None,
                "countdown_minutes": None,
                "countdown_display": "Unknown",
                "countdown_total_hours": None,
            }

        try:
            from datetime import datetime, timezone
            import re

            # Parse the ISO timestamp (handles various formats)
            if net_time.endswith("Z"):
                launch_time = datetime.fromisoformat(net_time.replace("Z", "+00:00"))
            elif "+" in net_time or net_time.count("-") > 2:
                launch_time = datetime.fromisoformat(net_time)
            else:
                # Assume UTC if no timezone info
                launch_time = datetime.fromisoformat(net_time + "+00:00")

            # Get current time in UTC
            now = datetime.now(timezone.utc)

            # Calculate time difference
            time_diff = launch_time - now
            total_seconds = time_diff.total_seconds()

            if total_seconds <= 0:
                return {
                    "countdown_days": 0,
                    "countdown_hours": 0,
                    "countdown_minutes": 0,
                    "countdown_display": "Launched",
                    "countdown_total_hours": 0,
                }

            # Calculate components
            days = int(total_seconds // 86400)  # 86400 seconds in a day
            remaining_seconds = total_seconds % 86400
            hours = int(remaining_seconds // 3600)  # 3600 seconds in an hour
            minutes = int((remaining_seconds % 3600) // 60)
            total_hours = total_seconds / 3600

            # Create display string
            if days > 0:
                if hours > 0:
                    countdown_display = f"{days}d {hours}h"
                else:
                    countdown_display = f"{days}d"
            elif hours > 0:
                if minutes > 0:
                    countdown_display = f"{hours}h {minutes}m"
                else:
                    countdown_display = f"{hours}h"
            else:
                countdown_display = f"{minutes}m"

            return {
                "countdown_days": days,
                "countdown_hours": hours,
                "countdown_minutes": minutes,
                "countdown_display": countdown_display,
                "countdown_total_hours": round(total_hours, 1),
            }

        except Exception as e:
            _LOGGER.warning("Error calculating countdown for %s: %s", net_time, e)
            return {
                "countdown_days": None,
                "countdown_hours": None,
                "countdown_minutes": None,
                "countdown_display": "Error",
                "countdown_total_hours": None,
            }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
