import asyncio
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, SWITCH_DEFINITIONS
from .entity import VistaPoolEntity

_LOGGER = logging.getLogger(__name__)


MANUAL_FILTRATION_REGISTER = 0x0413
EXEC_REGISTER = 0x02F5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up VistaPool switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id

    entities = []

    if not coordinator.data:
        _LOGGER.warning("VistaPool: No data from Modbus, skipping switch setup!")
        return

    for key, props in SWITCH_DEFINITIONS.items():
        # Only create relay switches if enabled in options
        option_key = props.get("option")
        if option_key and not entry.options.get(option_key, False):
            continue

        entities.append(VistaPoolSwitch(coordinator, entry_id, key, props))

    async_add_entities(entities)


class VistaPoolSwitch(VistaPoolEntity, SwitchEntity):
    """Representation of a VistaPool switch entity."""

    def __init__(self, coordinator, entry_id, key, props) -> None:
        """Initialize the VistaPool switch entity."""
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._switch_type = props.get("switch_type") or None
        self._relay_index = props.get("relay_index") or None
        self._attr_icon = props.get("icon") or None
        self._attr_entity_category = props.get("entity_category") or None
        self._icon_on = props.get("icon_on")
        self._icon_off = props.get("icon_off")
        self._attr_icon = props.get("icon") or None

        # Initialize properties for relay timer switches
        self.timer_block_addr = props.get("timer_block_addr") or None
        self.function_addr = props.get("function_addr") or None
        self.function_code = props.get("function_code") or None

        _LOGGER.debug(
            "VistaPoolSwitch INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch ON."""
        if self._switch_type == "manual_filtration":
            await self.coordinator.client.async_write_register(
                MANUAL_FILTRATION_REGISTER, 1
            )
        elif self._switch_type == "aux":
            _LOGGER.debug(f"Turning ON {self._key} (relay index {self._relay_index})")
            await self.coordinator.client.async_write_aux_relay(self._relay_index, True)
        elif self._switch_type == "auto_time_sync":
            await self.coordinator.set_auto_time_sync(True)
        elif self._switch_type == "relay_timer":
            client = self.coordinator.client
            _LOGGER.debug(
                f"Turning ON relay {self._key}: function_addr=0x{self.function_addr:04X}, timer_block_addr=0x{self.timer_block_addr:04X}"
            )
            await client.async_write_register(
                self.function_addr, self.function_code
            )  # Set function (if needed)
            await client.async_write_register(self.timer_block_addr, 3)  # Always on
            await client.async_write_register(EXEC_REGISTER, 1)  # Commit

        # Run a refresh to update the state
        await asyncio.sleep(1.0)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch OFF."""
        if self._switch_type == "manual_filtration":
            await self.coordinator.client.async_write_register(
                MANUAL_FILTRATION_REGISTER, 0
            )
        elif self._switch_type == "aux":
            _LOGGER.debug(f"Turning OFF {self._key} (relay index {self._relay_index})")
            await self.coordinator.client.async_write_aux_relay(
                self._relay_index, False
            )
        elif self._switch_type == "auto_time_sync":
            await self.coordinator.set_auto_time_sync(False)
        elif self._switch_type == "relay_timer":
            client = self.coordinator.client
            _LOGGER.debug(
                f"Turning OFF relay {self._key}: timer_block_addr=0x{self.timer_block_addr:04X}"
            )
            await client.async_write_register(self.timer_block_addr, 4)  # Always off
            await client.async_write_register(EXEC_REGISTER, 1)  # Commit

        # Run a refresh to update the state
        await asyncio.sleep(0.1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added to hass."""
        _LOGGER.debug(
            "VistaPoolSwitch ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        if self._switch_type == "manual_filtration":
            if self.coordinator.data.get("MBF_PAR_FILT_MODE") == 1:
                return False
            return self.coordinator.data.get("MBF_PAR_FILT_MANUAL_STATE") == 1
        elif self._switch_type == "aux":
            return bool(self.coordinator.data.get(self._key, False))
        elif self._switch_type == "auto_time_sync":
            return getattr(self.coordinator, "auto_time_sync", False)
        elif self._switch_type == "timer_enable":
            return bool(self.coordinator.data.get(self._key, 0))
        elif self._switch_type == "relay_timer":
            enable_val = self.coordinator.data.get(f"relay_{self._key}_enable", None)
            return enable_val == 3  # ON if ALWAYS ON
        return False

    @property
    def available(self) -> bool:
        """Return True if the switch is available."""
        if self._switch_type == "manual_filtration":
            return self.coordinator.data.get("MBF_PAR_FILT_MODE") != 1
        if self._switch_type == "relay_timer":
            # Getting the timer name based on the switch key (e.g., "aux1" -> "relay_aux1_enable")
            if self._key.startswith("aux"):
                timer_name = f"relay_{self._key}_enable"
            elif self._key == "light":
                timer_name = "relay_light_enable"
            else:
                return True
            mode_val = self.coordinator.data.get(timer_name, None)
            # 3 = on, 4 = off → available; 0 (disabled) or 1 (auto) → not available
            return mode_val in (3, 4)
        return True

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, depending on the state."""
        if self._icon_on and self._icon_off:
            return self._icon_on if self.is_on else self._icon_off
        if self._attr_icon:
            return self._attr_icon
        return None
