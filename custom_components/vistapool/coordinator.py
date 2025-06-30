import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_NAME

from .helpers import parse_version, prepare_device_time, is_device_time_out_of_sync
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, TIMER_BLOCKS

_LOGGER = logging.getLogger(__name__)


class VistaPoolCoordinator(DataUpdateCoordinator):
    """Coordinator for VistaPool platform."""

    def __init__(self, hass: HomeAssistant, client, entry, entry_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} coordinator",
            update_interval=timedelta(
                seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client
        self.entry = entry
        self.entry_id = entry_id
        self.device_name = entry.data.get(CONF_NAME, DOMAIN)
        self.auto_time_sync = self.entry.options.get("auto_time_sync", False)

    async def _async_update_data(self):
        try:
            data = await self.client.async_read_all()
            self._firmware = parse_version(data.get("MBF_POWER_MODULE_VERSION"))
            self._model = "VistaPool"
            # _LOGGER.debug("VistaPool raw coordinator data: %s", data)

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
            return data

        except Exception as err:
            _LOGGER.error("Modbus communication error: %s", err)
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
