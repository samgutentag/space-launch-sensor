"""Constants for the Space Launch Tracker integration."""

from datetime import timedelta

# Integration domain - must match the folder name
DOMAIN = "space_launch_sensor"

# Configuration keys
CONF_LAUNCH_LOCATION_ID = "launch_location_id"

# Default values
DEFAULT_NAME = "Upcoming Space Launch"
DEFAULT_LAUNCH_LOCATION_ID = 11  # Vandenberg SFB, CA, USA

# Update interval - how often to check for new data (default)
SCAN_INTERVAL = timedelta(hours=6)  # Default to 6 hours - launches don't change often

# API Configuration
API_BASE_URL = "https://ll.thespacedevs.com/2.2.0"
API_TIMEOUT = 10

# Sensor attributes that we'll expose
ATTR_LAUNCH_ID = "launch_id"
ATTR_LAUNCH_NAME = "launch_name"
ATTR_STATUS = "status"
ATTR_NET = "net"
ATTR_WINDOW_START = "window_start"
ATTR_WINDOW_END = "window_end"
ATTR_ROCKET = "rocket"
ATTR_MISSION = "mission"
ATTR_MISSION_TYPE = "mission_type"
ATTR_LAUNCH_PROVIDER = "launch_provider"
ATTR_LOCATION = "location"
ATTR_PAD = "pad"
ATTR_MAP_URL = "map_url"
ATTR_INFO_URL = "info_url"
ATTR_IMAGE_URL = "image_url"
