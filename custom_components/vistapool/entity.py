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

"""
VistaPool Integration for Home Assistant - Entity Module

This module defines the base entity class for the VistaPool integration.
It provides common functionality for all entities, including device information,
"""

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify as ha_slugify
from .helpers import parse_version, modbus_regs_to_hex_string
from .const import DOMAIN, NAME


class VistaPoolEntity(CoordinatorEntity):
    """Base class for VistaPool entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def translation_key(self) -> str | None:
        """Return the translation key for the entity."""
        return getattr(self, "_attr_translation_key", None)

    @property
    def device_info(self) -> dict:
        """Return device information for the entity."""
        serial_number = modbus_regs_to_hex_string(
            self.coordinator.data.get("MBF_POWER_MODULE_NODEID")
        )
        info = {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": getattr(self.coordinator, "device_name", NAME),
            "model": "NeoPool compatible",
            "manufacturer": "Sugar Valley",
            "hw_version": f"Detected Modules: [{self.decode_modules(self.coordinator.data.get("MBF_PAR_MODEL"))}]",
            "sw_version": f"v{self.coordinator.firmware} (v{parse_version(self.coordinator.data.get('MBF_PAR_VERSION'))})",
            "serial_number": serial_number,
        }
        return info

    # Generate a unique object ID for the entity to use in Home Assistant
    # This remove the prefix "mbf_" and "par_" from the key and replaces spaces, dashes, and dots with underscores
    @staticmethod
    def slugify(name) -> str:
        """Convert a name to a slug suitable for use as an object ID."""
        if not name:
            return ""
        return ha_slugify(name.lower().replace("mbf_", "", 1).replace("par_", "", 1))

    @staticmethod
    def decode_modules(model_bitmask) -> str:
        """Decode MBF_PAR_MODEL bitmask into a human-readable string."""
        if model_bitmask is None:
            return "Unknown"
        modules = []
        if model_bitmask & 0x0001:
            modules.append("Ionization")
        if model_bitmask & 0x0002:
            modules.append("Hydro/Electrolysis")
        if model_bitmask & 0x0004:
            modules.append("UV Lamp")
        if model_bitmask & 0x0008:
            modules.append("Salinity")
        return ", ".join(modules) if modules else "None"
