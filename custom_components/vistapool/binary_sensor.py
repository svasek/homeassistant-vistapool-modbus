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
        _LOGGER.warning("VistaPool: No data from Modbus, skipping binary_sensor setup!")
        return

    for key, props in BINARY_SENSOR_DEFINITIONS.items():
        option_key = props.get("option")
        if option_key and not entry.options.get(option_key, False):
            continue
        # Skip sensors that are not detected
        if key.startswith("ION ") and not bool(
            (coordinator.data.get("MBF_PAR_MODEL") or 0) & 0x0001
        ):
            continue
        # Hide all "measurement module detected" sensors
        if "measurement module detected" in key.lower():
            continue
        # Skip the base pump if the relay is not assigned
        if (
            key == "pH pump active"
            and coordinator.data.get("MBF_PAR_PH_BASE_RELAY_GPIO") is not True
        ):
            continue
        # Skip the acid pump if the relay is not assigned
        if (
            key == "pH acid pump active"
            and coordinator.data.get("MBF_PAR_PH_ACID_RELAY_GPIO") is not True
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
                        if not coordinator.data.get(data_key):
                            skip_entity = True
                            break
                if skip_entity:
                    break
        if skip_entity:
            continue  # Skip this entity

        entities.append(
            VistaPoolBinarySensor(
                coordinator,
                entry.entry_id,  # Pass entry_id explicitly
                key,  # Pass key as a positional argument
                props,
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
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_device_class = props.get("device_class") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._icon_on = props.get("icon_on") or None
        self._icon_off = props.get("icon_off") or None

        # Disable some entities by default.
        if (
            self._attr_suggested_object_id.endswith("_measurement_active")
            or self._attr_suggested_object_id.endswith("_pump_active")
            or self._attr_suggested_object_id.endswith("_acid_pump")
            or self._attr_suggested_object_id.endswith("_shock_mode")
            or self._attr_suggested_object_id.endswith("_on_target")
            or self._attr_suggested_object_id.endswith("_low_flow")
            or self._attr_suggested_object_id.endswith("_input_active")
            or self._attr_suggested_object_id.endswith("_indicator_fl2")
        ):
            self._attr_entity_registry_enabled_default = False

        _LOGGER.debug(
            "VistaPoolBinarySensor INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

        # Generate unique ID based on the bit name
        key_parts = self._key.split("_")
        if len(key_parts) > 1:
            bit = key_parts[1].lower()
        else:
            bit = self._key.lower()

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            "VistaPoolBinarySensor ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        if self._key == "Device Time Out Of Sync":
            return is_device_time_out_of_sync(self.coordinator.data, self.hass)
        parts = self._key.split("_", 1)

        # Check if the filtration pump is active
        if self._attr_suggested_object_id.endswith(
            "_measurement_active"
        ) or self._attr_suggested_object_id.endswith("_module_active"):
            filtration_state = self.coordinator.data.get("Filtration Pump")
            if filtration_state is not None and filtration_state is False:
                return False

        if len(parts) == 2:
            base, flag = parts
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
