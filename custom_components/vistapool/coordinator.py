import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_NAME

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class VistaPoolCoordinator(DataUpdateCoordinator):
    """Coordinator for VistaPool platform."""
    def __init__(self, hass: HomeAssistant, client, entry, entry_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} coordinator",
            update_interval=timedelta(seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)),
        )
        self.client = client
        self.entry = entry
        self.entry_id = entry_id
        self.device_name = entry.data.get(CONF_NAME, DOMAIN)

    
    @property
    def firmware(self) -> str:
        return self._firmware

    @property
    def model(self) -> str:
        return self._model

    async def _async_update_data(self):
        try:
            data = await self.client.async_read_all()
            self._firmware = self.parse_version(data.get("MBF_POWER_MODULE_VERSION"))
            self._model = "VistaPool"
            # _LOGGER.debug("VistaPool raw coordinator data: %s", data)
            return data

        except Exception as err:
            raise ConfigEntryNotReady(f"Error fetching data: {err}") from err

    @staticmethod
    def parse_version(val):
        if isinstance(val, int):
            major = (val >> 8) & 0xFF
            minor = val & 0xFF
            return f"{major}.{minor:02d}"
        return "?"