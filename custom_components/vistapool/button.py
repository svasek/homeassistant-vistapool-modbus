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

"""VistaPool Integration for Home Assistant - Button Module"""

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, BUTTON_DEFINITIONS
from .coordinator import VistaPoolCoordinator
from .entity import VistaPoolEntity
from .helpers import prepare_device_time

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

    if not coordinator.data:
        _LOGGER.warning("VistaPool: No data from Modbus, skipping button setup!")
        return

    for key, props in BUTTON_DEFINITIONS.items():
        entities.append(VistaPoolButton(coordinator, entry_id, key, props))
    async_add_entities(entities)


class VistaPoolButton(VistaPoolEntity, ButtonEntity):
    """Representation of a VistaPool button entity."""

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the VistaPool button entity."""
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = (
            f"{self.coordinator.device_slug}_{VistaPoolEntity.slugify(self._key)}"
        )
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_entity_category = props.get("entity_category") or None
        self._attr_icon = props.get("icon") or "mdi:button-pointer"

        _LOGGER.debug(
            "VistaPoolButton INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_press(self) -> None:
        """Perform button action depending on key."""
        if self._key == "SYNC_TIME":
            client = self.coordinator.client
            _LOGGER.debug("Syncing time with device...")
            await client.async_write_register(0x0408, prepare_device_time(self.hass))
            await client.async_write_register(0x04F0, 1)
            await self.coordinator.async_request_refresh()
        elif self._key == "MBF_ESCAPE":
            client = self.coordinator.client
            _LOGGER.debug("Clearing all possible errors...")
            await client.async_write_register(0x0297, 1)
            await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            "VistaPoolButton ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def icon(self) -> str | None:
        """Return the icon for the button."""
        return self._attr_icon
