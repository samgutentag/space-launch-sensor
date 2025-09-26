# Space Launch Sensor

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-shield]][hacs]

A Home Assistant integration that tracks upcoming space launches from specific locations using The Space Devs API.

**This integration will set up the following platforms:**

| Platform | Description                                                      |
| -------- | ---------------------------------------------------------------- |
| `sensor` | Show upcoming space launch information with countdown attributes |

![Example](https://github.com/yourusername/space-launch-sensor/raw/main/example.png)

## Features

- Track upcoming launches from any launch location worldwide
- Rich attributes including mission details, rocket info, and launch pad data
- Built-in countdown calculations (days, hours, minutes until launch)
- Automatic updates every 6 hours (configurable)
- Default configured for Vandenberg Space Force Base
- Perfect for creating countdown badges and detailed launch cards

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL and select "Integration" as category
5. Click "Install" on the Space Launch Sensor integration
6. Restart Home Assistant

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
2. If you do not have a `custom_components` directory (folder) there, you need to create it
3. In the `custom_components` directory (folder) create a new folder called `space_launch_sensor`
4. Download _all_ the files from the `custom_components/space_launch_sensor/` directory (folder) in this repository
5. Place the files you downloaded in the new directory (folder) you created
6. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: space_launch_sensor
    name: "My Space Launch Sensor"
    launch_location_id: 11 # Vandenberg SFB (default)
    scan_interval: 21600 # 6 hours (default: 6 hours)
```

### Configuration Variables

- **name** (optional): Custom name for the sensor
- **launch_location_id** (optional): Launch location ID from The Space Devs API (default: 11 for Vandenberg SFB)
- **scan_interval** (optional): Update frequency in seconds (default: 21600 = 6 hours)

### Finding Location IDs

To find launch location IDs, visit: https://ll.thespacedevs.com/2.2.0/location/
Popular locations:

- **11**: Vandenberg SFB, CA, USA
- **12**: Kennedy Space Center, FL, USA
- **16**: Baikonur Cosmodrome, Kazakhstan
- **27**: Mahia Peninsula, New Zealand (Rocket Lab)
- **143**: Kourou, French Guiana (Ariane, Vega)

### Update Frequency Options

Choose your scan_interval based on your needs:

- **1800** (30 minutes): For frequent updates when launches are imminent
- **21600** (6 hours): Recommended default - good balance of freshness and API courtesy
- **86400** (24 hours): For minimal API usage when you just want daily updates

Example configurations:

```yaml
# Frequent updates during active launch periods
sensor:
  - platform: space_launch_sensor
    name: "Active Launch Tracking"
    launch_location_id: 12  # Kennedy Space Center
    scan_interval: 1800     # 30 minutes

# Standard daily monitoring (recommended)
sensor:
  - platform: space_launch_sensor
    name: "Daily Launch Updates"
    scan_interval: 21600    # 6 hours
```

## Sensor Attributes

The sensor provides these attributes:

- `launch_id`: Unique launch identifier
- `status`: Launch status (Go, TBD, etc.)
- `net`: No Earlier Than timestamp
- `window_start` / `window_end`: Launch window
- `rocket`: Full rocket name
- `mission`: Mission name and type
- `launch_provider`: Company conducting the launch
- `location`: Launch pad location and name
- `map_url`: Link to launch pad location
- `info_url`: Link to detailed launch information
- `image_url`: Mission patch or launch image

### Countdown Attributes

The sensor also calculates countdown information:

- `countdown_days`: Days until launch
- `countdown_hours`: Hours remaining (after days)
- `countdown_minutes`: Minutes remaining (after hours)
- `countdown_display`: Formatted countdown (e.g., "5d 8h" or "2h 30m")
- `countdown_total_hours`: Total time until launch in hours

## Dashboard Examples

### Countdown Badge

Create a countdown badge that only appears when a launch is approaching:

```yaml
# Add to configuration.yaml
template:
  - sensor:
      - name: "Launch Countdown Badge"
        unique_id: "launch_countdown_badge"
        state: "{{ state_attr('sensor.your_sensor_name', 'countdown_display') }}"
        icon: >-
          {% set days = state_attr('sensor.your_sensor_name', 'countdown_days') | int(0) %}
          {% if days <= 1 %}
            mdi:rocket-launch
          {% elif days <= 7 %}
            mdi:rocket
          {% else %}
            mdi:rocket-outline
          {% endif %}

# Dashboard card
type: entity
entity: sensor.launch_countdown_badge
name: "🚀 Next Launch"
visibility:
  - condition: template
    value_template: "{{ states('sensor.launch_countdown_badge') not in ['Launched', 'Error', 'Unknown'] }}"
```

### Detailed Launch Card

```yaml
type: entities
title: 🚀 Next Space Launch
entities:
  - entity: sensor.your_sensor_name
    name: Mission
    icon: mdi:rocket
  - type: attribute
    entity: sensor.your_sensor_name
    attribute: rocket
    name: Rocket
    icon: mdi:rocket-launch
  - type: attribute
    entity: sensor.your_sensor_name
    attribute: status
    name: Status
    icon: mdi:clock-outline
  - type: attribute
    entity: sensor.your_sensor_name
    attribute: countdown_display
    name: Time Until Launch
    icon: mdi:timer-outline
```

## Data Source

This integration uses [The Space Devs API](https://thespacedevs.com/) for launch data.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This integration was developed for the Home Assistant community.

---

[space-launch-sensor]: https://github.com/yourusername/space-launch-sensor
[commits-shield]: https://img.shields.io/github/commit-activity/y/yourusername/space-launch-sensor.svg?style=for-the-badge
[commits]: https://github.com/yourusername/space-launch-sensor/commits/main
[hacs]: https://github.com/hacs/integration
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/yourusername/space-launch-sensor.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/yourusername/space-launch-sensor.svg?style=for-the-badge
[releases]: https://github.com/yourusername/space-launch-sensor/releases
