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

"""VistaPool Integration for Home Assistant - Sensor Module"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, SENSOR_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity
from .helpers import get_filtration_pump_type, calculate_next_interval_time

_LOGGER = logging.getLogger(__name__)

# Add mapping for MBF_PAR_FILT_MODE values
# fmt: off
FILTRATION_MODE_MAP = {
    0: "manual",        # This mode allows to turn the filtration (and all other systems that depend on it) on and off manually
    1: "auto",          # This mode allows filtering to be turned on and off according to the settings of the TIMER1, TIMER2 and TIMER3 timers.
    2: "heating",       # This mode is similar to the AUTO mode, but includes setting the temperature for the heating function. This mode is activated only if the MBF_PAR_HEATING_MODE register is at 1 and there is a heating relay assigned.
    3: "smart",         # This filtration mode adjusts the pump operating times depending on the temperature. This mode is activated only if the MBF_PAR_TEMPERATURE_ACTIVE register is at 1.
    4: "intelligent",   # This mode performs an intelligent filtration process in combination with the heating function. This mode is activated only if the MBF_PAR_HEATING_MODE register is at 1 and there is a heating relay assigned.
    13: "backwash",     # This filter mode is started when the backwash operation is activated.
}
# fmt: on

FILTRATION_SPEED_MAP = {
    0: "off",
    1: "low",
    2: "mid",
    3: "high",
}

PH_STATUS_ALARM_MAP = {
    0: "no_alarm",
    1: "ph_high",
    2: "ph_low",
    3: "ph_stopped",
    4: "ph_over",
    5: "ph_under",
    6: "tank_level",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VistaPool sensors from a config entry."""
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if not coordinator.data:  # pragma: no cover
        _LOGGER.warning("No data from Modbus, skipping sensor setup!")
        return

    # Loop through the defined sensors and create SensorEntity instances
    for key, props in SENSOR_DEFINITIONS.items():
        # Skip the sensors if they are not detected
        if (
            key == "MBF_MEASURE_TEMPERATURE"
            and coordinator.data.get("MBF_PAR_TEMPERATURE_ACTIVE") == 0
        ):
            continue
        if (
            key == "MBF_MEASURE_PH"
            and coordinator.data.get("pH measurement module detected") is not True
        ):
            continue
        if (
            key == "MBF_MEASURE_RX"
            and coordinator.data.get("Redox measurement module detected") is not True
        ):
            continue
        if (
            key == "MBF_MEASURE_CL"
            and coordinator.data.get("Chlorine measurement module detected") is not True
        ):
            continue
        if (
            key == "MBF_MEASURE_CONDUCTIVITY"
            and coordinator.data.get("Conductivity measurement module detected")
            is not True
        ):
            continue
        if key == "MBF_ION_CURRENT" and not bool(
            (coordinator.data.get("MBF_PAR_MODEL") or 0) & 0x0001
        ):
            continue
        if key == "FILTRATION_SPEED" and not get_filtration_pump_type(
            coordinator.data.get("MBF_PAR_FILTRATION_CONF", 0)
        ):
            continue
        if (
            key == "MBF_PAR_INTELLIGENT_INTERVALS"
            or key == "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL"
        ):
            # Skip if heating GPIO not assigned or temperature inactive
            if (
                not bool(coordinator.data.get("MBF_PAR_HEATING_GPIO"))
                or coordinator.data.get("MBF_PAR_TEMPERATURE_ACTIVE") == 0
            ):
                continue

        value = coordinator.data.get(key)
        if (
            isinstance(value, (int, float))
            or key == "MBF_PAR_FILT_MODE"
            or key == "MBF_PH_STATUS_ALARM"
            or key == "HIDRO_POLARITY"
        ):
            entities.append(
                VistaPoolSensor(
                    coordinator, entry.entry_id, key, props  # Pass entry_id explicitly
                )
            )
    async_add_entities(entities)


class VistaPoolSensor(VistaPoolEntity, SensorEntity):
    """Representation of a VistaPool sensor."""

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the VistaPool sensor entity."""
        super().__init__(coordinator, entry_id)  # Pass entry_id to the parent class
        self._key = key
        self._attr_suggested_object_id = (
            f"{self.coordinator.device_slug}_{VistaPoolEntity.slugify(self._key)}"
        )
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_native_unit_of_measurement = props.get("unit") or None
        self._attr_device_class = props.get("device_class") or None
        self._attr_state_class = props.get("state_class") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._attr_icon = props.get("icon") or None

        # Disable some entities by default.
        if self._attr_suggested_object_id.endswith("_voltage"):  # pragma: no cover
            self._attr_entity_registry_enabled_default = False

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
    def icon(self) -> str | None:
        raw = self.coordinator.data.get(self._key)
        # Filtration mode icons
        if self._key == "MBF_PAR_FILT_MODE":
            mode = FILTRATION_MODE_MAP.get(raw)
            if mode == "auto":
                return "mdi:water-boiler-auto"
            elif mode == "manual":
                return "mdi:water-boiler-alert"
            elif mode == "heating":
                return "mdi:water-boiler"
            elif mode == "smart":
                return "mdi:water-boiler-check"
            elif mode == "intelligent":
                return "mdi:water-boiler-thermometer"
            elif mode == "backwash":
                return "mdi:water-boiler-off"
        # PH alarm icons
        if self._key == "MBF_PH_STATUS_ALARM":
            status = PH_STATUS_ALARM_MAP.get(raw)
            if status == "no_alarm":
                return "mdi:check-circle-outline"
            else:
                return "mdi:alert"
        if self._key == "MBF_HIDRO_CURRENT":
            return (
                "mdi:air-humidifier"
                if bool(self.coordinator.data.get(self._key))
                else "mdi:air-humidifier-off"
            )
        return self._attr_icon or None

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested display precision for the sensor value."""
        if self._key == "MBF_HIDRO_CURRENT":
            return 0
        if self._key == "MBF_MEASURE_CONDUCTIVITY":
            return 0
        return None

    @property
    def native_value(self) -> float | int | str | None:
        """Return the actual sensor value from coordinator data."""

        # If filtration is not running, some sensors should not return a value
        # This is to avoid showing stale or irrelevant data when filtration is off
        # For example, temperature, pH, RX, conductivity, and voltage sensors
        # These sensors are only relevant when the filtration pump is running
        # Anyway, we allow to override this behavior in the options
        measure_when_off = self.coordinator.config_entry.options.get(
            "measure_when_filtration_off", False
        )
        if (
            self._key
            in {
                "MBF_MEASURE_TEMPERATURE",
                "MBF_MEASURE_PH",
                "MBF_MEASURE_RX",
                "MBF_MEASURE_CONDUCTIVITY",
                "MBF_HIDRO_VOLTAGE",
                "FILTRATION_SPEED",
            }
            and not measure_when_off
        ):
            filtration_state = self.coordinator.data.get("Filtration Pump")
            if filtration_state is not None and filtration_state is False:
                return None

        # Polarity sensor created from two binary sensors
        if self._key == "HIDRO_POLARITY":
            pol1 = self.coordinator.data.get("HIDRO in Pol1")
            pol2 = self.coordinator.data.get("HIDRO in Pol2")
            if pol1:
                return "pol1"
            elif pol2:
                return "pol2"
            return "off"
        if self._key == "MBF_PAR_FILT_MODE":
            raw = self.coordinator.data.get(self._key)
            return FILTRATION_MODE_MAP.get(raw)
        if self._key == "FILTRATION_SPEED":
            raw = self.coordinator.data.get(self._key)
            return FILTRATION_SPEED_MAP.get(raw)
        if self._key == "MBF_PH_STATUS_ALARM":
            raw = self.coordinator.data.get(self._key)
            return PH_STATUS_ALARM_MAP.get(raw)
        if self._key == "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL":
            # Convert seconds to timestamp using helper function
            seconds = self.coordinator.data.get(self._key)
            return calculate_next_interval_time(seconds, self.hass)
        return self.coordinator.data.get(self._key)

    @property
    def options(self) -> list[str] | None:
        """Return the list of options for the sensor."""
        if self._key == "MBF_PAR_FILT_MODE":
            return list(FILTRATION_MODE_MAP.values())
        if self._key == "FILTRATION_SPEED":
            return list(FILTRATION_SPEED_MAP.values())
        if self._key == "MBF_PH_STATUS_ALARM":
            return list(PH_STATUS_ALARM_MAP.values())
        if self._key == "HIDRO_POLARITY":
            return ["pol1", "pol2", "off"]
        return None  # pragma: no cover

    @property
    def available(self) -> bool:
        """Return True if the sensor should be available (based on filtration state)."""
        return True
