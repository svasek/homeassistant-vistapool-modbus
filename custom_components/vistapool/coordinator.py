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

"""VistaPool Integration for Home Assistant - Coordinator Module"""

import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_NAME
import json

from .helpers import parse_version, prepare_device_time, is_device_time_out_of_sync
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    TIMER_BLOCKS,
    HEATING_SETPOINT_REGISTER,
    INTELLIGENT_SETPOINT_REGISTER,
)

MAX_SCAN_INTERVAL = timedelta(seconds=180)  # Maximum allowed scan interval (3 minutes)

_LOGGER = logging.getLogger(__name__)


class VistaPoolCoordinator(DataUpdateCoordinator):
    """Coordinator for VistaPool platform."""

    def __init__(self, hass: HomeAssistant, client, entry, entry_id: str):
        # Store normal and maximal intervals
        self.normal_update_interval = timedelta(
            seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        )
        self.max_update_interval = min(
            self.normal_update_interval * 4, MAX_SCAN_INTERVAL
        )
        self._consecutive_errors = 0

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} coordinator",
            update_interval=self.normal_update_interval,
            config_entry=entry,
        )
        self.client = client
        self.entry = entry
        self.entry_id = entry_id
        self.device_name = entry.data.get(CONF_NAME, DOMAIN)
        self.auto_time_sync = self.entry.options.get("auto_time_sync", False)

    async def _async_update_data(self):
        try:
            data = await self.client.async_read_all()
            self._consecutive_errors = 0

            # Reset interval after success
            if self.update_interval != self.normal_update_interval:  # pragma: no cover
                _LOGGER.info(
                    f"Communication OK, resetting update interval to {self.normal_update_interval.total_seconds()} seconds."
                )
                self.update_interval = self.normal_update_interval

            self._firmware = parse_version(data.get("MBF_POWER_MODULE_VERSION"))
            self._model = "VistaPool"

            options = self.entry.options
            enabled_timers = []
            # Collect enabled timers based on options
            # This assumes that the options are set correctly in the config entry
            for key in TIMER_BLOCKS:
                if key.startswith("relay_aux"):
                    n = key[len("relay_aux")]
                    option_key = f"use_aux{n}"
                elif key == "relay_light":
                    option_key = "use_light"
                else:
                    option_key = f"use_{key}"
                if options.get(option_key, False):
                    enabled_timers.append(key)

            timers = await self.client.read_all_timers(enabled_timers=enabled_timers)

            for t_name, t in timers.items():
                data[f"{t_name}_enable"] = t["enable"]
                data[f"{t_name}_start"] = t["on"]  # saved as seconds since midnight
                data[f"{t_name}_interval"] = t["interval"]
                data[f"{t_name}_period"] = t["period"]
                if t["on"] is not None and t["interval"] is not None:
                    stop = (t["on"] + t["interval"]) % 86400
                    data[f"{t_name}_stop"] = stop
                else:
                    data[f"{t_name}_stop"] = None

            if self.auto_time_sync:
                if is_device_time_out_of_sync(data, self.hass):
                    _LOGGER.debug("Device time is out of sync, updating...")
                    await self.client.async_write_register(
                        0x0408, prepare_device_time(self.hass)
                    )
                    await self.client.async_write_register(0x04F0, 1)

            # Apply developer overrides (for testing UI visibility without hardware)
            try:
                if self.entry.options.get("dev_overrides_enabled", False):
                    raw = self.entry.options.get("dev_overrides", "{}")
                    overrides = json.loads(raw) if isinstance(raw, str) else raw
                    if isinstance(overrides, dict):
                        for k, v in overrides.items():
                            data[k] = v
                        _LOGGER.debug("Applied dev overrides: %s", overrides)
                    else:  # pragma: no cover
                        _LOGGER.warning("dev_overrides must be a JSON object (dict)")
            except Exception as dev_err:  # pragma: no cover
                _LOGGER.warning("Failed to apply dev_overrides: %s", dev_err)

            # Keep heating and intelligent setpoints synchronized based on the last change.
            # If exactly one changed since the previous snapshot and values differ now,
            # mirror the changed value into the other register (last-change-wins).
            # If both changed at once, revert both to previous values to avoid conflicts.
            # If neither changed but they differ, sync intelligent to heating (initial sync).
            try:
                prev = getattr(self, "data", None)
                heat = data.get("MBF_PAR_HEATING_TEMP")
                intel = data.get("MBF_PAR_INTELLIGENT_TEMP")
                if heat is not None and intel is not None and heat != intel:
                    h_old = prev.get("MBF_PAR_HEATING_TEMP") if prev else None
                    i_old = prev.get("MBF_PAR_INTELLIGENT_TEMP") if prev else None
                    heating_changed = h_old is None or heat != h_old
                    intelligent_changed = i_old is None or intel != i_old

                    if heating_changed ^ intelligent_changed:
                        # Exactly one changed: sync the other to match (last-change-wins)
                        winner_val = int(heat if heating_changed else intel)
                        loser_reg = (
                            INTELLIGENT_SETPOINT_REGISTER
                            if heating_changed
                            else HEATING_SETPOINT_REGISTER
                        )
                        await self.client.async_write_register(
                            loser_reg, winner_val, apply=True
                        )
                        # Reflect in returned data so HA shows synced values immediately
                        data["MBF_PAR_HEATING_TEMP"] = winner_val
                        data["MBF_PAR_INTELLIGENT_TEMP"] = winner_val
                        _LOGGER.debug(
                            "Auto-synced setpoints (last-change-wins) -> heating=%s, intelligent=%s",
                            data["MBF_PAR_HEATING_TEMP"],
                            data["MBF_PAR_INTELLIGENT_TEMP"],
                        )
                    elif heating_changed and intelligent_changed:
                        # Both changed this cycle; revert both to previous values
                        _LOGGER.warning(
                            "Both heating and intelligent setpoints changed simultaneously "
                            "(heating: %s→%s, intelligent: %s→%s). Reverting both to previous values to prevent conflict.",
                            h_old,
                            heat,
                            i_old,
                            intel,
                        )
                        if h_old is not None and i_old is not None:
                            # Write both back to their old values
                            await self.client.async_write_register(
                                HEATING_SETPOINT_REGISTER, int(h_old), apply=False
                            )
                            await self.client.async_write_register(
                                INTELLIGENT_SETPOINT_REGISTER, int(i_old), apply=True
                            )
                            # Reflect revert in returned data
                            data["MBF_PAR_HEATING_TEMP"] = h_old
                            data["MBF_PAR_INTELLIGENT_TEMP"] = i_old
                            _LOGGER.debug(
                                "Reverted setpoints -> heating=%s, intelligent=%s",
                                data["MBF_PAR_HEATING_TEMP"],
                                data["MBF_PAR_INTELLIGENT_TEMP"],
                            )
                    elif not heating_changed and not intelligent_changed:
                        # Neither changed but they differ: initial sync (use heating as source)
                        _LOGGER.info(
                            "Setpoints differ but neither changed (heating=%s, intelligent=%s). "
                            "Performing initial sync: setting intelligent to match heating.",
                            heat,
                            intel,
                        )
                        await self.client.async_write_register(
                            INTELLIGENT_SETPOINT_REGISTER, int(heat), apply=True
                        )
                        # Reflect in returned data
                        data["MBF_PAR_INTELLIGENT_TEMP"] = heat
                        _LOGGER.debug(
                            "Initial sync completed -> heating=%s, intelligent=%s",
                            data["MBF_PAR_HEATING_TEMP"],
                            data["MBF_PAR_INTELLIGENT_TEMP"],
                        )
            except Exception as sync_err:  # pragma: no cover
                _LOGGER.debug(f"Setpoint auto-sync skipped due to error: {sync_err}")
            return data

        except Exception as err:
            self._consecutive_errors += 1
            _LOGGER.error(f"Modbus communication error: {err}")

            # Exponential backoff: double the interval, but never more than max
            next_interval = self.update_interval * 2
            if next_interval > self.max_update_interval:  # pragma: no cover
                next_interval = self.max_update_interval
            if self.update_interval != next_interval:
                _LOGGER.warning(
                    f"Increasing update interval to {int(next_interval.total_seconds())} seconds due to communication errors."
                )
                self.update_interval = next_interval

            # Fallback: use cached data if available
            # This allows the integration to continue functioning with cached data
            # if the Modbus communication fails, but only if we have cached data
            # This is useful for scenarios where the device might be temporarily unreachable
            # or if the Modbus server is down, but we still want to use the last known good data
            if getattr(self, "data", None):
                _LOGGER.warning("Using cached data due to Modbus error")
                return self.data
            raise ConfigEntryNotReady(f"Error fetching data: {err}") from err

    async def set_auto_time_sync(self, enabled: bool):
        self.auto_time_sync = enabled
        # Update the entry options to reflect the change
        # This is necessary to persist the setting across restarts
        # and to ensure that the coordinator uses the updated value
        # when fetching data
        options = dict(self.entry.options)
        options["auto_time_sync"] = enabled
        self.hass.config_entries.async_update_entry(self.entry, options=options)

    @property
    def firmware(self) -> str:
        return self._firmware

    @property
    def model(self) -> str:
        return self._model

    @property
    def device_slug(self):  # pragma: no cover
        return self.config_entry.unique_id or slugify(self.device_name)
