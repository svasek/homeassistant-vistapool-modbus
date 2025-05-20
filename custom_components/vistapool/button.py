import logging
import datetime
import homeassistant.util.dt as dt_util
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, BUTTON_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VistaPool button entities from a config entry."""
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []
    for key, props in BUTTON_DEFINITIONS.items():
        entities.append(
            VistaPoolButton(
                coordinator,
                entry_id,
                key,
                props.get("name"),
                props.get("icon"),
                props.get("entity_category"),
            )
        )
    async_add_entities(entities)

class VistaPoolButton(VistaPoolEntity, ButtonEntity):
    def __init__(self, coordinator, entry_id, key, name, icon=None, entity_category=None):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)
        
        self._attr_entity_category = entity_category
        self._attr_icon = icon or "mdi:button-pointer"

        _LOGGER.debug(
            "VistaPoolButton INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )

    async def async_press(self) -> None:
        """Perform button action depending on key."""
        if self._key == "SYNC_TIME":
            ha_tz = dt_util.get_time_zone(self.hass.config.time_zone)
            now_local = datetime.datetime.now(ha_tz)
            # WORKAROUND: This is the naive datetime object, without timezone info
            epoch_local = datetime.datetime(1970, 1, 1, tzinfo=ha_tz)
            unix_time_local = int((now_local - epoch_local).total_seconds())
            low = unix_time_local & 0xFFFF
            high = (unix_time_local >> 16) & 0xFFFF
            client = self.coordinator.client
            await client.async_write_register(0x0408, [low, high])
            await client.async_write_register(0x04F0, 1)
            await self.coordinator.async_request_refresh()

    @property
    def icon(self):
        return self._attr_icon

    async def async_added_to_hass(self):
        _LOGGER.debug(
            "VistaPoolButton ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id, self._attr_translation_key, getattr(self, "has_entity_name", None)
        )
        await super().async_added_to_hass()