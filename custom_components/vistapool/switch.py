import asyncio
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, SWITCH_DEFINITIONS
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)


MANUAL_FILTRATION_REGISTER = 0x0413

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up VistaPool switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []

    for key, props in SWITCH_DEFINITIONS.items():
        # Only create AUX switches if enabled in options
        if props.get("switch_type") == "aux" and not entry.options.get(props["option"], False):
            continue
        entities.append(
            VistaPoolSwitch(
                coordinator,
                entry_id,
                key,
                props.get("name"),
                props.get("icon"),
                props.get("switch_type"),
                props.get("entity_category"),
                props.get("relay_index"),
            )
        )

    async_add_entities(entities)

class VistaPoolSwitch(VistaPoolEntity, SwitchEntity):
    def __init__(
        self, coordinator, entry_id, key, name, icon, switch_type, entity_category=None, relay_index=None
    ):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)
        
        self._switch_type = switch_type
        self._relay_index = relay_index
        self._attr_icon = icon or None
        self._attr_entity_category = entity_category
        
        _LOGGER.debug(
            "VistaPoolSwitch INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )

    async def async_turn_on(self, **kwargs):
        if self._switch_type == "manual_filtration":
            await self.coordinator.client.async_write_register(MANUAL_FILTRATION_REGISTER, 1)
        elif self._switch_type == "aux":
            _LOGGER.debug(f"Turning ON {self._key} (relay index {self._relay_index})")
            await self.coordinator.client.async_write_aux_relay(self._relay_index, True)
        elif self._switch_type == "auto_time_sync":
            await self.coordinator.set_auto_time_sync(True)
            
        # Run a refresh to update the state
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        if self._switch_type == "manual_filtration":
            await self.coordinator.client.async_write_register(MANUAL_FILTRATION_REGISTER, 0)
        elif self._switch_type == "aux":
            _LOGGER.debug(f"Turning OFF {self._key} (relay index {self._relay_index})")
            await self.coordinator.client.async_write_aux_relay(self._relay_index, False)
        elif self._switch_type == "auto_time_sync":
            await self.coordinator.set_auto_time_sync(False)

        # Run a refresh to update the state
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        _LOGGER.debug(
            "VistaPoolSwitch ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )
        await super().async_added_to_hass()
        
        
    @property
    def is_on(self):
        if self._switch_type == "manual_filtration":
            if self.coordinator.data.get("MBF_PAR_FILT_MODE") == 1:
                return False
            return self.coordinator.data.get("MBF_PAR_FILT_MANUAL_STATE") == 1
        elif self._switch_type == "aux":
            return bool(self.coordinator.data.get(self._key, False))
        elif self._switch_type == "auto_time_sync":
            return getattr(self.coordinator, "auto_time_sync", False)
        return False

    @property
    def available(self) -> bool:
        if self._switch_type == "manual_filtration":
            return self.coordinator.data.get("MBF_PAR_FILT_MODE") != 1
        return True

    @property
    def icon(self):
        return self._attr_icon