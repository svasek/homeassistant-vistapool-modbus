import logging
import asyncio
from homeassistant.components.select import SelectEntity
from .const import DOMAIN, SELECT_DEFINITIONS
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)

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
                props.get("name"),
                props.get("icon"),
                props.get("options_map"),
                props.get("register"),
            )
        )
    async_add_entities(entities)

class VistaPoolSelect(VistaPoolEntity, SelectEntity):
    def __init__(self, coordinator, entry_id, key, name, icon, options_map, register):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)
        
        self._attr_icon = icon
        self._options_map = options_map
        self._register = register
        
        _LOGGER.debug(
            "VistaPoolSelect INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )

    async def async_select_option(self, option: str):
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
            await self.coordinator.client.async_write_register(self._register, value)
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
        return list(self._options_map.values())

    @property
    def current_option(self):
        value = self.coordinator.data.get(self._key)
        return self._options_map.get(value)