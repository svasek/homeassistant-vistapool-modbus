# Copyright 2025 Miloš Svašek

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""VistaPool Integration for Home Assistant - Binary Sensor Module"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, BINARY_SENSOR_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity
from .helpers import is_device_time_out_of_sync

_LOGGER = logging.getLogger(__name__)

DISABLED_SUFFIXES = [
    " measurement active",
    " pump active",
    " Acid Pump",
    " shock mode",
    " On Target",
    " Low Flow",
    " input active",
    " indicator FL2",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VistaPool binary sensors from a config entry."""
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    SUFFIXES = (
        "flow sensor problem",
        "module control status",
        "control status",
        "pump active",
        "control module",
        "measurement active",
    )
    entities = []

    if not coordinator.data:
        _LOGGER.warning("No data from Modbus, skipping binary_sensor setup!")
        return

    for key, props in BINARY_SENSOR_DEFINITIONS.items():
        sensor_props = dict(props)
        option_key = sensor_props.get("option")
        if option_key and not entry.options.get(option_key, False):
            continue
        # Skip sensors that are not detected
        if key.startswith("ION ") and not bool(
            (coordinator.data.get("MBF_PAR_MODEL") or 0) & 0x0001
        ):
            continue  # pragma: no cover
        # Hide all "measurement module detected" sensors
        if "measurement module detected" in key.lower():
            continue
        # Skip the base pump if the relay is not assigned
        if key == "pH pump active" and not bool(
            coordinator.data.get("MBF_PAR_PH_BASE_RELAY_GPIO")
        ):
            continue
        # Skip the acid pump if the relay is not assigned
        if key == "pH acid pump active" and not bool(
            coordinator.data.get("MBF_PAR_PH_ACID_RELAY_GPIO")
        ):
            continue
        # Skip chlorine related sensors
        if (
            key.endswith("Activated by the CL module")
            and coordinator.data.get("Chlorine measurement module detected") is not True
        ):
            continue
        # Skip redox related sensors
        if (
            key.endswith("Activated by the RX module")
            and coordinator.data.get("Redox measurement module detected") is not True
        ):
            continue
        # Skip Pool Cover if not enabled in device configuration
        if key == "Pool Cover" and not bool(
            (coordinator.data.get("MBF_PAR_HIDRO_COVER_ENABLE") or 0) & 0x0001
        ):
            continue

        # Check if the entity should be skipped based on the suffixes
        # Hide selected sensors if their 'measurement module detected' status is False.
        skip_entity = False
        key_lower = key.lower()
        for suffix in SUFFIXES:
            if key_lower.endswith(suffix):
                prefix = key_lower[: -len(suffix)].strip()
                for data_key in coordinator.data:
                    if data_key.lower().startswith(
                        prefix
                    ) and data_key.lower().endswith("measurement module detected"):
                        if not coordinator.data.get(data_key):  # pragma: no cover
                            skip_entity = True
                            break
                if skip_entity:  # pragma: no cover
                    break
        if skip_entity:  # pragma: no cover
            continue  # Skip this entity

        # Check if the entity should be enabled by default
        # Disable some entities by default based on their key
        if any(key.lower().endswith(suf) for suf in DISABLED_SUFFIXES):
            sensor_props["enabled_default"] = False
        else:
            sensor_props["enabled_default"] = True

        entities.append(
            VistaPoolBinarySensor(
                coordinator,
                entry.entry_id,  # Pass entry_id explicitly
                key,  # Pass key as a positional argument
                sensor_props,
            )
        )
    async_add_entities(entities)


class VistaPoolBinarySensor(VistaPoolEntity, BinarySensorEntity):
    """Representation of a VistaPool binary sensor."""

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id)
        self._key = key
        self._bit = None
        self._base = None

        # Parse key if it is a status flag (e.g., "PH_STATUS_regulating")
        if "_STATUS_" in key:
            self._base, self._bit = key.split("_STATUS_", 1)

        self._key = key
        self._attr_suggested_object_id = (
            f"{self.coordinator.device_slug}_{VistaPoolEntity.slugify(self._key)}"
        )
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_device_class = props.get("device_class") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._icon_on = props.get("icon_on") or None
        self._icon_off = props.get("icon_off") or None

        self._attr_entity_registry_enabled_default = props.get("enabled_default", True)

        _LOGGER.debug(
            f"INIT: suggested_object_id={self._attr_suggested_object_id}, translation_key={self._attr_translation_key}, has_entity_name={getattr(self, 'has_entity_name', None)}"
        )

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            f"ADDED: entity_id={self.entity_id}, translation_key={self._attr_translation_key}, has_entity_name={getattr(self, 'has_entity_name', None)}"
        )
        await super().async_added_to_hass()

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        if self._key == "Device Time Out Of Sync":
            return is_device_time_out_of_sync(self.coordinator.data, self.hass)

        # Pool Cover: Invert logic for OPENING device class
        # Hardware: 1 = cover active (pool covered), 0 = cover inactive (pool uncovered)
        # HA OPENING: ON = open (uncovered), OFF = closed (covered)
        if self._key == "Pool Cover":
            value = self.coordinator.data.get(self._key)
            return not bool(value)

        # Check if the filtration pump is active
        if self._attr_suggested_object_id.endswith(
            "_measurement_active"
        ) or self._attr_suggested_object_id.endswith("_module_active"):
            filtration_state = self.coordinator.data.get("Filtration Pump")
            if filtration_state is not None and filtration_state is False:
                return False

        if "_STATUS_" in self._key:
            base, flag = self._key.split("_STATUS_", 1)
            status = self.coordinator.data.get(f"{base}_STATUS", {})
            if isinstance(status, dict):
                return status.get(flag.lower(), False)
            else:
                return False
        else:
            value = self.coordinator.data.get(self._key)
            return bool(value)

    @property
    def icon(self) -> str | None:
        """Return custom icon depending on state."""
        return self._icon_on if self.is_on else self._icon_off or None

    @property
    def native_value(self) -> bool | None:
        """Return the actual sensor value."""
        # Return the actual sensor value from coordinator data
        return self.coordinator.data.get(self._key)
