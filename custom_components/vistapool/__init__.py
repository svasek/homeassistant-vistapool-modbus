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

"""VistaPool Integration for Home Assistant"""

import logging
from homeassistant.helpers import config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.exceptions import ServiceValidationError
from .const import DOMAIN, PLATFORMS
from .modbus import VistaPoolModbusClient
from .coordinator import VistaPoolCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the VistaPool integration."""

    # --- MIGRATE CONFIG FLOW DATA TO OPTIONS IF NEEDED ---
    # Copy all keys except connection settings from data to options
    connection_keys = [CONF_HOST, CONF_PORT, CONF_NAME, "slave_id"]
    candidate_keys = [k for k in entry.data if k not in connection_keys]
    if not entry.options or not any(k in entry.options for k in candidate_keys):
        new_options = {k: entry.data[k] for k in candidate_keys}
        if new_options:  # pragma: no cover
            _LOGGER.debug(
                "VistaPool: Migrating ALL config entry data (except connection params) to options: %s",
                new_options,
            )
            hass.config_entries.async_update_entry(entry, options=new_options)
    # --- End migration ---

    # Initialize Modbus client and coordinator
    client = VistaPoolModbusClient(entry.data)
    coordinator = VistaPoolCoordinator(hass, client, entry, entry.entry_id)

    # Wait for the first update from the coordinator
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator and client in hass.data for easy access
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward entities setup to Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a VistaPool config entry."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator and getattr(coordinator, "client", None):
        await coordinator.client.close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        # Cleanup services when last entry is removed
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "set_timer")
    return unload_ok


async def async_setup(hass, config) -> bool:
    """Set up the VistaPool integration."""
    from .helpers import get_timer_interval, hhmm_to_seconds

    # Register the service to set timers
    async def async_handle_set_timer(call) -> None:
        """Handle the set_timer service call."""
        try:
            timer_name = call.data["timer"]
            start = call.data.get("start")
            stop = call.data.get("stop")
            enable = call.data.get("enable")
            entry_id = call.data.get("entry_id")
            period = call.data.get("period")
            if not entry_id:
                # fallback: if entry_id is not provided, use the first entry_id in hass.data[DOMAIN]
                entry_id = next(iter(hass.data[DOMAIN]), None)
            if not entry_id:
                raise ValueError("No entry_id found for VistaPool service call")
            coordinator = hass.data[DOMAIN][entry_id]
            # Convert start and stop times to seconds
            start_sec = hhmm_to_seconds(start) if start else None
            stop_sec = hhmm_to_seconds(stop) if stop else None
            interval = (
                get_timer_interval(start_sec, stop_sec) if (start and stop) else None
            )

            # Prepare the timer data as a dictionary
            timer_data = {}
            if start_sec is not None:
                timer_data["on"] = start_sec
            if interval is not None:
                timer_data["interval"] = interval
            if period is not None:
                timer_data["period"] = int(period)
            if enable is not None:
                timer_data["enable"] = enable

            _LOGGER.debug("Setting timer %s with data: %s", timer_name, timer_data)
            await coordinator.client.write_timer(timer_name, timer_data)
            await coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(
                "Failed to set timer %s: %s", call.data.get("timer", "unknown"), e
            )
            raise ServiceValidationError(f"Timer setting failed: {e}")

    hass.services.async_register(DOMAIN, "set_timer", async_handle_set_timer)
    return True
