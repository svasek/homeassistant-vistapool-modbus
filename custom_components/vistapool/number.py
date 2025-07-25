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

"""VistaPool Integration for Home Assistant - Number Module"""

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
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up VistaPool number entities from a config entry."""
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []

    if not coordinator.data:
        _LOGGER.warning("VistaPool: No data from Modbus, skipping number setup!")
        return

    for key, props in NUMBER_DEFINITIONS.items():
        # Conditionally add heating setpoint only if heating relay is assigned
        if key == "MBF_PAR_HEATING_TEMP":
            if not bool(coordinator.data.get("MBF_PAR_HEATING_GPIO")):
                continue
        # Conditionally add pH high limit only if acid pump relay is assigned
        if key == "MBF_PAR_PH1":
            if not bool(coordinator.data.get("MBF_PAR_PH_ACID_RELAY_GPIO")):
                continue
        # Conditionally add pH low limit only if base pump relay is assigned
        if key == "MBF_PAR_PH2":
            if not bool(coordinator.data.get("MBF_PAR_PH_BASE_RELAY_GPIO")):
                continue
        # Conditionally add redox setpoint only if redox relay is assigned
        if key == "MBF_PAR_RX1":
            if not bool(coordinator.data.get("Redox measurement module detected")):
                continue
        # Conditionally add chlorine setpoint only if chlorine pump relay is assigned
        if key == "MBF_PAR_CL1":
            if not bool(coordinator.data.get("Chlorine measurement module detected")):
                continue

        entities.append(VistaPoolNumber(coordinator, entry_id, key, props))

    async_add_entities(entities)


class VistaPoolNumber(VistaPoolEntity, NumberEntity):
    """Representation of a VistaPool number entity."""

    _pending_write_task = None
    _pending_value = None
    _debounce_delay = 2.0

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the VistaPool number entity."""
        super().__init__(coordinator, entry_id)
        self._key = key
        self._register = props.get("register", None)
        self._scale = props.get("scale", 1.0)

        self._attr_suggested_object_id = (
            f"{self.coordinator.device_slug}_{VistaPoolEntity.slugify(self._key)}"
        )
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_native_unit_of_measurement = props.get("unit", None)
        self._attr_native_min_value = props.get("min", None)
        self._attr_native_max_value = props.get("max", None)
        self._attr_native_step = props.get("step", 1.0)
        self._attr_mode = "box"

        self._attr_device_class = props.get("device_class") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._attr_icon = props.get("icon")

        _LOGGER.debug(
            "VistaPoolNumber INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            "VistaPoolNumber ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        client = getattr(self.coordinator, "client", None)
        if client is None:
            _LOGGER.error(
                "VistaPoolNumber: Modbus client not available for reading registers."
            )
            return
        await super().async_added_to_hass()

        # Read full register map and get the value using string key
        data = await client.async_read_all()
        raw = data.get(self._key)
        if raw is not None:
            self._attr_native_value = round(raw, 2)
        else:
            self._attr_native_value = None

        self.async_write_ha_state()

    async def async_set_native_value(self, value: float | int | str) -> None:
        """Set the native value of the number entity."""
        self._pending_value = value
        if self._pending_write_task is not None and not self._pending_write_task.done():
            self._pending_write_task.cancel()
        self._pending_write_task = asyncio.create_task(self._debounced_write())
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def _debounced_write(self) -> None:
        """Debounced write to the Modbus register."""
        client = getattr(self.coordinator, "client", None)
        if client is None:
            _LOGGER.error(
                "VistaPoolNumber: Modbus client not available for writing registers."
            )
            return
        try:
            await asyncio.sleep(self._debounce_delay)
            raw = int(self._pending_value * self._scale)
            await client.async_write_register(self._register, raw, apply=True)
            await self.coordinator.async_request_refresh()
        except asyncio.CancelledError:
            pass

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested display precision for the number value."""
        if self._key == "MBF_PAR_HIDRO":
            return 0
        if self._key == "MBF_PAR_HEATING_TEMP":
            return 0
        return None

    @property
    def icon(self) -> str | None:
        """Return custom icon depending on state."""
        return self._attr_icon or None

    @property
    def native_value(self) -> float | int | str | None:
        """Return the actual number value."""
        raw = self.coordinator.data.get(self._key)
        if self.suggested_display_precision == 0 and raw is not None:
            return int(round(raw))
        if raw is None:
            return self._attr_native_value  # fallback if coordinator is not updated yet
        return round(raw, 2)

    # Property to set correct native value for hydrolysis
    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement for the number value."""
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
    def native_max_value(self) -> float | None:
        """Return the maximum value for the number entity."""
        if self._key == "MBF_PAR_HIDRO":
            hidro_nom = self.coordinator.data.get("MBF_PAR_HIDRO_NOM")
            if hidro_nom is not None:
                return hidro_nom
        return self._attr_native_max_value
