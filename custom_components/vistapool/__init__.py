import logging
from homeassistant.helpers import config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .modbus import VistaPoolModbusClient
from .coordinator import VistaPoolCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the VistaPool integration."""
    # Initialize Modbus client and coordinator
    client = VistaPoolModbusClient(entry.data)
    coordinator = VistaPoolCoordinator(hass, client, entry, entry.entry_id)

    # Wait for the first update from the coordinator
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator and client in hass.data for easy access
    # hass.data.setdefault(DOMAIN, {})
    # hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward entities setup to Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a VistaPool config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_setup(hass, config):
    from .helpers import get_timer_interval, hhmm_to_seconds

    # Register the service to set timers
    async def async_handle_set_timer(call):
        timer_name = call.data["timer"]
        start = call.data.get("start")
        stop = call.data.get("stop")
        enable = call.data.get("enable")
        entry_id = call.data.get("entry_id")
        if not entry_id:
            # fallback: if entry_id is not provided, use the first entry_id in hass.data[DOMAIN]
            entry_id = next(iter(hass.data[DOMAIN]), None)
        if not entry_id:
            raise ValueError("No entry_id found for VistaPool service call")
        coordinator = hass.data[DOMAIN][entry_id]
        # Convert start and stop times to seconds
        start_sec = hhmm_to_seconds(start) if start else None
        stop_sec = hhmm_to_seconds(stop) if stop else None
        interval = get_timer_interval(start_sec, stop_sec) if (start and stop) else None

        # Prepare the timer data as a dictionary
        timer_data = {}
        if start_sec is not None:
            timer_data["on"] = start_sec
        if interval is not None:
            timer_data["interval"] = interval
        if enable is not None:
            timer_data["enable"] = enable

        _LOGGER.debug("Setting timer %s with data: %s", timer_name, timer_data)
        await coordinator.client.write_timer(timer_name, timer_data)
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "set_timer", async_handle_set_timer)
    return True
