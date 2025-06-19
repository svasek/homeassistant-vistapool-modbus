import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, SENSOR_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity
from .helpers import get_device_time, get_filtration_pump_type

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

    if not coordinator.data:
        _LOGGER.warning("VistaPool: No data from Modbus, skipping sensor setup!")
        return

    # Loop through the defined sensors and create SensorEntity instances
    for key, props in SENSOR_DEFINITIONS.items():
        # Skip the sensors if they are not detected
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
        if (
            key == "FILTRATION_SPEED"
            and get_filtration_pump_type(
                coordinator.data.get("MBF_PAR_FILTRATION_CONF", 0)
            )
            is not True
        ):
            continue

        value = coordinator.data.get(key)
        if (
            isinstance(value, (int, float))
            or key == "MBF_PAR_FILT_MODE"
            or key == "MBF_PH_STATUS_ALARM"
            or key == "HIDRO_POLARITY"
            or key == "MBF_DEVICE_TIME"
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
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_native_unit_of_measurement = props.get("unit") or None
        self._attr_unit_of_measurement = props.get("unit") or None
        self._attr_device_class = props.get("device_class") or None
        self._attr_state_class = props.get("state_class") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._attr_icon = props.get("icon") or None

        # Disable some entities by default.
        if self._attr_suggested_object_id.endswith("_voltage"):
            self._attr_entity_registry_enabled_default = False

        _LOGGER.debug(
            "VistaPoolSensor INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            "VistaPoolSensor ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def icon(self) -> str | None:
        """Return custom icon depending on state."""
        if self._key == "MBF_PAR_FILT_MODE":
            raw = self.coordinator.data.get(self._key)
            if FILTRATION_MODE_MAP.get(raw) == "Auto":
                return "mdi:water-boiler-auto"
            elif FILTRATION_MODE_MAP.get(raw) == "Manual":
                return "mdi:water-boiler-alert"
            elif FILTRATION_MODE_MAP.get(raw) == "Heating":
                return "mdi:water-boiler"
            elif FILTRATION_MODE_MAP.get(raw) == "Smart":
                return "mdi:water-boiler-check"
            elif FILTRATION_MODE_MAP.get(raw) == "Intelligent":
                return "mdi:water-boiler-thermometer"
            elif FILTRATION_MODE_MAP.get(raw) == "Backwash":
                return "mdi:water-boiler-off"
        if self._key == "MBF_PH_STATUS_ALARM":
            raw = self.coordinator.data.get(self._key)
            if PH_STATUS_ALARM_MAP.get(raw) == "No Alarm":
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
        if self._key == "MBF_DEVICE_TIME":
            return get_device_time(self.coordinator.data, self.hass)
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
        return None

    @property
    def available(self) -> bool:
        """Return True if the sensor should be available (based on filtration state)."""
        # Sensors that only make sense when filtration is running
        _flow_dependent_keys = {
            "MBF_MEASURE_TEMPERATURE",
            "MBF_MEASURE_PH",
            "MBF_MEASURE_RX",
            "MBF_MEASURE_CONDUCTIVITY",
            "MBF_HIDRO_VOLTAGE",
            "FILTRATION_SPEED",
        }
        if self._key in _flow_dependent_keys:
            # Check if the filtration pump is running (binary_sensor "Filtration Pump" must be ON)
            filtration_state = self.coordinator.data.get("Filtration Pump")
            if filtration_state is not None:
                return filtration_state is True
            return False  # unknown state, so not available
        return True
