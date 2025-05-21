import logging
import asyncio
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, NUMBER_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up VistaPool number entities from a config entry."""
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []
    for definition in NUMBER_DEFINITIONS:
        # Conditionally add heating setpoint only if heating relay is assigned
        if definition["key"] == "MBF_PAR_HEATING_TEMP":
            if not bool(coordinator.data.get("MBF_PAR_HEATING_GPIO")):
                continue
        # Conditionally add pH high limit only if acid pump relay is assigned
        if definition["key"] == "MBF_PAR_PH1":
            if not bool(coordinator.data.get("MBF_PAR_PH_ACID_RELAY_GPIO")):
                continue
        # Conditionally add pH low limit only if base pump relay is assigned
        if definition["key"] == "MBF_PAR_PH2":
            if not bool(coordinator.data.get("MBF_PAR_PH_BASE_RELAY_GPIO")):
                continue
        # Conditionally add redox setpoint only if redox relay is assigned
        if definition["key"] == "MBF_PAR_RX1":
            if not bool(coordinator.data.get("Redox measurement module detected")):
                continue
        # Conditionally add chlorine setpoint only if chlorine pump relay is assigned
        if definition["key"] == "MBF_PAR_CL1":
            if not bool(coordinator.data.get("Chlorine measurement module detected")):
                continue
        entities.append(VistaPoolNumber(coordinator, entry_id, definition))
    async_add_entities(entities)


class VistaPoolNumber(VistaPoolEntity, NumberEntity):
    _pending_write_task = None
    _pending_value = None
    _debounce_delay = 2.0
    
    def __init__(self, coordinator, entry_id, definition):
        super().__init__(coordinator, entry_id)
        self._definition = definition
        self._register = definition["register"]
        self._key = definition["key"]
        self._scale = definition["scale"]

        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)
        
        self._attr_native_unit_of_measurement = definition["unit"]
        self._attr_native_min_value = definition["min"]
        self._attr_native_max_value = definition["max"]
        self._attr_native_step = definition["step"]
        self._attr_mode = "box"
        
        self._attr_device_class = definition.get("device_class") or None
        self._attr_entity_category = definition.get("entity_category") or None
        self._attr_icon = definition.get("icon")
    
        _LOGGER.debug(
            "VistaPoolNumber INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        # Read full register map and get the value using string key
        data = await self.coordinator.client.async_read_all()
        raw = data.get(self._key)
        if raw is not None:
            self._attr_native_value = round(raw, 2)
        else:
            self._attr_native_value = None

        self.async_write_ha_state()
        
    async def async_set_native_value(self, value):
        self._pending_value = value
        if self._pending_write_task is not None and not self._pending_write_task.done():
            self._pending_write_task.cancel()
        self._pending_write_task = asyncio.create_task(self._debounced_write())
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
    
    async def _debounced_write(self):
        try:
            await asyncio.sleep(self._debounce_delay)
            raw = int(self._pending_value * self._scale)
            await self.coordinator.client.async_write_register(self._register, raw, apply=True)
            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            pass

    async def async_added_to_hass(self):
        _LOGGER.debug(
            "VistaPoolNumber ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )
        await super().async_added_to_hass()


    @property
    def suggested_display_precision(self):
        if self._key == "MBF_PAR_HIDRO":
            return 0
        if self._key == "MBF_PAR_HEATING_TEMP":
            return 0
        return None
    
    @property
    def icon(self):
        """Return custom icon depending on state."""
        return self._attr_icon or None

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if self.suggested_display_precision == 0 and raw is not None:
            return int(round(raw))
        if raw is None:
            return self._attr_native_value  # fallback if coordinator is not updated yet
        return round(raw, 2)
    
    # Property to set correct native value for hydrolysis
    @property
    def native_unit_of_measurement(self):
        if self._key == "MBF_PAR_HIDRO":
            hidro_nom = self.coordinator.data.get("MBF_PAR_HIDRO_NOM")
            if hidro_nom is not None:
                if hidro_nom == 100.0:
                    return "%"
                else:
                    return "g/h"
        return self._attr_native_unit_of_measurement

    # Property to set correct native max value for hydrolysis
    @property
    def native_max_value(self):
        if self._key == "MBF_PAR_HIDRO":
            hidro_nom = self.coordinator.data.get("MBF_PAR_HIDRO_NOM")
            if hidro_nom is not None:
                return hidro_nom
        return self._attr_native_max_value