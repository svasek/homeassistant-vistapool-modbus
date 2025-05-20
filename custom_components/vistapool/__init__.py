import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SENSOR_DEFINITIONS, BINARY_SENSOR_DEFINITIONS, DEFAULT_SCAN_INTERVAL
from .modbus import VistaPoolModbusClient
from .sensor import VistaPoolSensor
from .binary_sensor import VistaPoolBinarySensor
from .coordinator import VistaPoolCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the VistaPool integration."""
    # Initialize Modbus client and coordinator
    client = VistaPoolModbusClient(entry.data)

    async def async_update_data():
        try:
            return await client.async_read_all()
        except Exception as err:
            _LOGGER.error("Error communicating with VistaPool device: %s", err)
            raise UpdateFailed(err)

    coordinator = VistaPoolCoordinator(hass, client, entry, entry.entry_id)

    # Wait for the first update from the coordinator
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator and client in hass.data for easy access
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator 

    # Register sensors and binary sensors
    entities = []
    
    for key, definition in SENSOR_DEFINITIONS.items():
        name = definition.get("name")
        unit = definition.get("unit")
        device_class = definition.get("device_class")
        state_class = definition.get("state_class")
        entity_category = definition.get("entity_category")
        icon = definition.get("icon") or None,

        entities.append(
            VistaPoolSensor(
                coordinator,
                key,
                name,
                unit,
                device_class,
                state_class,
                entity_category=entity_category,
                icon=icon,
            )
        )
    
    for key, definition in BINARY_SENSOR_DEFINITIONS.items():
        name = definition.get("name")
        device_class = definition.get("device_class")
        entity_category = definition.get("entity_category")
        icon_on = definition.get("icon_on")
        icon_off = definition.get("icon_off")

        entities.append(
            VistaPoolBinarySensor(
                coordinator,
                key,
                name,
                device_class,
                entity_category=entity_category,
                icon_on=icon_on,
                icon_off=icon_off,
            )
        )
    
    # Forward entities setup to Home Assistant
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "switch", "number", "button", "select"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a VistaPool config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "binary_sensor", "switch", "number"]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
