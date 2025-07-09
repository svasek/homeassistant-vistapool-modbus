import asyncio
import logging
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, LIGHT_DEFINITIONS
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)


EXEC_REGISTER = 0x02F5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up VistaPool lights from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []

    if not coordinator.data:
        _LOGGER.warning("VistaPool: No data from Modbus, skipping light setup!")
        return

    for key, props in LIGHT_DEFINITIONS.items():
        # Only create light if enabled in options
        option_key = props.get("option")
        if option_key and not entry.options.get(option_key, False):
            continue

        entities.append(VistaPoolLight(coordinator, entry_id, key, props))

    async_add_entities(entities)


class VistaPoolLight(VistaPoolEntity, LightEntity):
    """Representation of a VistaPool light entity."""

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the VistaPool light entity."""
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

        self._switch_type = props.get("switch_type") or None
        self._attr_icon = props.get("icon") or None
        self._icon_on = props.get("icon_on")
        self._icon_off = props.get("icon_off")

        # Initialize properties for relay timer switches
        self.timer_block_addr = props.get("timer_block_addr") or None
        self.function_addr = props.get("function_addr") or None
        self.function_code = props.get("function_code") or None

        _LOGGER.debug(
            "VistaPoolLight INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light ON."""
        client = getattr(self.coordinator, "client", None)
        if client is None:
            _LOGGER.error(
                "VistaPoolLight: Modbus client not available for writing registers."
            )
            return
        if self._switch_type == "relay_timer":
            _LOGGER.debug(
                f"Turning ON {self._key}: function_addr=0x{self.function_addr:04X}, timer_block_addr=0x{self.timer_block_addr:04X}"
            )
            await client.async_write_register(
                self.function_addr, self.function_code
            )  # Set function (if needed)
            await client.async_write_register(self.timer_block_addr, 3)  # Always ON
            await client.async_write_register(EXEC_REGISTER, 1)  # Commit

        # Run a refresh to update the state
        await asyncio.sleep(2.0)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light OFF."""
        client = getattr(self.coordinator, "client", None)
        if client is None:
            _LOGGER.error(
                "VistaPoolLight: Modbus client not available for writing registers."
            )
            return
        if self._switch_type == "relay_timer":
            _LOGGER.debug(
                f"Turning OFF {self._key}: timer_block_addr=0x{self.timer_block_addr:04X}"
            )
            await client.async_write_register(self.timer_block_addr, 4)  # Always OFF
            await client.async_write_register(EXEC_REGISTER, 1)  # Commit

        # Run a refresh to update the state
        await asyncio.sleep(2.0)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when the entity is added to hass."""
        _LOGGER.debug(
            "VistaPoolLight ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def is_on(self) -> bool:
        """Return True if the light is ON."""
        if self._switch_type == "relay_timer":
            enable_val = self.coordinator.data.get("relay_light_enable", None)
            return enable_val == 3  # ON if ALWAYS ON
        return False

    @property
    def available(self) -> bool:
        """Return True if the light is available."""
        if self._switch_type == "relay_timer":
            mode_val = self.coordinator.data.get("relay_light_enable", None)
            return mode_val in (0, 3, 4)
        return True

    @property
    def icon(self) -> str | None:
        """Return custom icon depending on state."""
        if self._icon_on and self._icon_off:
            return self._icon_on if self.is_on else self._icon_off
        if self._attr_icon:
            return self._attr_icon
        return None

    @property
    def supported_color_modes(self) -> set[str]:
        """Return the color modes supported by this light."""
        # For simple on/off light, the correct mode is COLOR_MODE_ONOFF (or ColorMode.ONOFF)
        return {"onoff"}

    @property
    def color_mode(self) -> str:
        """Return the current color mode of the light."""
        # Actual mode is always onoff, as brightness and color are not available
        return "onoff"
