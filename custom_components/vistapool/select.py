import logging
import asyncio
from homeassistant.components.select import SelectEntity
from .const import DOMAIN, SELECT_DEFINITIONS
from .entity import VistaPoolEntity
from .helpers import seconds_to_hhmm

_LOGGER = logging.getLogger(__name__)


MANUAL_FILTRATION_REGISTER = 0x0413

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    entities = []
    for key, props in SELECT_DEFINITIONS.items():
        entities.append(
            VistaPoolSelect(
                coordinator,
                entry_id,
                key,
                props
            )
        )
    async_add_entities(entities)

class VistaPoolSelect(VistaPoolEntity, SelectEntity):
    def __init__(self, coordinator, entry_id, key, props):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)
        
        self._attr_icon = props.get("icon") or None
        self._options_map = props.get("options_map") or {}
        self._attr_entity_category = props.get("entity_category") or None
        self._select_type = props.get("select_type") or None
        self._register = props.get("register") or None
        
        _LOGGER.debug(
            "VistaPoolSelect INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )

    async def async_select_option(self, option: str):
        if self._select_type == "timer_time":
            timer_name, field = self._key.rsplit("_", 1)
            entry_id = self._entry_id if hasattr(self, '_entry_id') else self.coordinator.entry_id
            data = self.coordinator.data
            if field == "start":
                start = option
                stop = seconds_to_hhmm(data.get(f"{timer_name}_stop", 0))
            elif field == "stop":
                start = seconds_to_hhmm(data.get(f"{timer_name}_start", 0))
                stop = option
            else:
                return

            await self.hass.services.async_call(
                DOMAIN,
                "set_timer",
                {
                    "entry_id": entry_id,
                    "timer": timer_name,
                    "start": start,
                    "stop": stop,
                }
            )
            await asyncio.sleep(0.2)
            await self.coordinator.async_request_refresh()
            self.async_write_ha_state()
            return
        
        # Prevent switching to Backwash from HA UI
        if option == "backwash":
            # Log warning
            _LOGGER.warning("Cannot switch to Backwash from Home Assistant UI.")
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "message": "Cannot switch to Backwash from Home Assistant. Please use device display instead.",
                    "title": "VistaPool Warning"
                }
            )
            return
        
        value = None
        for k, v in self._options_map.items():
            if v == option:
                value = k
                break
            
        if value is not None:
            # Special: MBF_PAR_FILT_MODE needs to handle manual → other
            # We have to turn off manual filtration first (set register 0x0413 to 0)
            # and then set the new mode
            if self._key == "MBF_PAR_FILT_MODE":
                current_mode = self.coordinator.data.get(self._key)
                current_name = self._options_map.get(current_mode)
                if current_name == "manual" and option != "manual":
                    await self.coordinator.client.async_write_register(MANUAL_FILTRATION_REGISTER, 0)
                    await asyncio.sleep(0.1)
            # Set the new mode
            await self.coordinator.client.async_write_register(self._register, value)
            await asyncio.sleep(0.1)
            await self.coordinator.async_request_refresh()
            
        # Run a refresh to update the state
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        _LOGGER.debug(
            "VistaPoolSelect ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )
        await super().async_added_to_hass()


    @property
    def options(self):
        options = list(self._options_map.values())
        
        # Hide heating and intelligent if not enabled heating mode
        if self._key == "MBF_PAR_FILT_MODE" and self.coordinator.data.get("MBF_PAR_HEATING_MODE") == 0:
            options = [opt for opt in options if opt not in ("heating", "intelligent")]
        # Hide smart if temperature sensor is not active
        if self._key == "MBF_PAR_FILT_MODE" and self.coordinator.data.get("MBF_PAR_TEMPERATURE_ACTIVE") == 0:
            options = [opt for opt in options if opt != "smart"]
            
        # Handle Timer options in cases where doesn't fit 15 minutes
        if self._select_type == "timer_time":
            value = self.coordinator.data.get(self._key)
            if value is not None:
                current_hhmm = seconds_to_hhmm(value)
                if current_hhmm not in options:
                    return [current_hhmm] + options
        return options


    @property
    def current_option(self):
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        if self._options_map:
            # If not exactly in options_map, always return current HH:MM
            return self._options_map.get(value) or seconds_to_hhmm(value)
        return seconds_to_hhmm(value)