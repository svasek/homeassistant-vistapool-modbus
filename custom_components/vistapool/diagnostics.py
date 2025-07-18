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

"""VistaPool Integration for Home Assistant - Diagnostics Module"""

from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for a VistaPool config entry."""

    diagnostics: dict = {}

    # Basic config and options (without any sensitive data)
    diagnostics["config_entry"] = {
        "data": {
            k: v
            for k, v in entry.data.items()
            if "password" not in k and "token" not in k
        },
        "options": dict(entry.options),
        "title": entry.title,
        "entry_id": entry.entry_id,
        "version": entry.version,
    }

    # Coordinator state (contains data, errors, etc.)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    diagnostics["coordinator"] = {
        "last_update_success": getattr(coordinator, "last_update_success", None),
        "last_update_time": str(getattr(coordinator, "last_update_time", None)),
        "data": getattr(coordinator, "data", {}),
        "update_interval": str(getattr(coordinator, "update_interval", None)),
        "last_exception": str(getattr(coordinator, "last_exception", "")),
        "firmware": getattr(coordinator, "firmware", None),
        "model": getattr(coordinator, "model", None),
        "client": str(getattr(coordinator, "client", "")),
    }

    # Additional client details
    client = getattr(coordinator, "client", None)
    if client:
        diagnostics["client"] = {
            "host": getattr(client, "host", None),
            "port": getattr(client, "port", None),
            "unit": getattr(client, "unit_id", None),
            "connected": getattr(client, "connected", None),
            "last_error": str(getattr(client, "last_error", "")),
        }

    if client and hasattr(client, "connection_stats"):
        diagnostics["connection_stats"] = client.connection_stats

    return diagnostics
