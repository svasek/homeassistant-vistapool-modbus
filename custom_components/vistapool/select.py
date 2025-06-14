import logging
import asyncio
from homeassistant.components.select import SelectEntity
from .const import DOMAIN, SELECT_DEFINITIONS
from .entity import VistaPoolEntity
from .helpers import seconds_to_hhmm, get_filtration_pump_type

_LOGGER = logging.getLogger(__name__)


MANUAL_FILTRATION_REGISTER = 0x0413


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    entities = []

    for key, props in SELECT_DEFINITIONS.items():
        # Skip the selects if they are not detected
        if key == "MBF_PAR_FILTRATION_SPEED" and not bool(
            get_filtration_pump_type(coordinator.data.get("MBF_PAR_FILTRATION_CONF", 0))
        ):
            continue
        # Skip boost mode select if model does not support "Hydro/Electrolysis"
        if key == "MBF_CELL_BOOST":
            mbf_par_model = coordinator.data.get("MBF_PAR_MODEL", 0)
            if not (mbf_par_model & 0x0002):
                continue

        entities.append(VistaPoolSelect(coordinator, entry_id, key, props))
    async_add_entities(entities)


class VistaPoolSelect(VistaPoolEntity, SelectEntity):
    def __init__(self, coordinator, entry_id, key, props):
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_suggested_object_id = f"{VistaPoolEntity.slugify(self.coordinator.device_name)}_{VistaPoolEntity.slugify(self._key)}"
        self.entity_id = f"{self.platform}.{self._attr_suggested_object_id}"
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self._key.lower()}"
        )
        self._attr_translation_key = VistaPoolEntity.slugify(self._key)

        self._attr_icon = props.get("icon") or None
        self._options_map = props.get("options_map") or {}
        self._attr_entity_category = props.get("entity_category") or None
        self._select_type = props.get("select_type") or None
        self._register = props.get("register") or None
        self._attr_mask = props.get("mask") or None
        self._attr_shift = props.get("shift") or None

        _LOGGER.debug(
            "VistaPoolSelect INIT: suggested_object_id=%s, translation_key=%s, has_entity_name=%s",
            self._attr_suggested_object_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )

    async def async_select_option(self, option: str):
        if self._select_type == "timer_time":
            timer_name, field = self._key.rsplit("_", 1)
            entry_id = (
                self._entry_id
                if hasattr(self, "_entry_id")
                else self.coordinator.entry_id
            )
            data = self.coordinator.data
            if field == "start":
                start = option
                stop = seconds_to_hhmm(data.get(f"{timer_name}_stop", 0))
            elif field == "stop":
                start = seconds_to_hhmm(data.get(f"{timer_name}_start", 0))
                stop = option
            else:
                return

            await self.hass.services.async_call(
                DOMAIN,
                "set_timer",
                {
                    "entry_id": entry_id,
                    "timer": timer_name,
                    "start": start,
                    "stop": stop,
                },
            )
            await asyncio.sleep(0.2)
            return

        if option == "backwash":
            # Log info about backwash
            _LOGGER.info(
                'Your pool "%s" has been switched to the BACKWASH mode!',
                VistaPoolEntity.slugify(self.coordinator.device_name),
            )
            return

        if self._key == "MBF_CELL_BOOST":
            value = None
            for k, v in self._options_map.items():
                if v == option:
                    value = k
                    break

            reg = SELECT_DEFINITIONS[self._key]["register"]
            if value is not None:
                if value == 0:
                    write_val = 0
                elif value == 1:
                    write_val = (
                        0x0500 | 0x00A0 | 0x8000
                    )  # 0x85A0 = Boost active, redox control DISABLED
                elif value == 2:
                    write_val = (
                        0x0500 | 0x00A0
                    )  # 0x05A0 = Boost active, redox control ENABLED
                else:
                    return

                await self.coordinator.client.async_write_register(reg, write_val)
                await asyncio.sleep(0.2)
            return

        if self._key == "MBF_PAR_FILTRATION_SPEED":
            rev_map = {v: k for k, v in self._options_map.items()}
            value = rev_map.get(option)
            if value is None:
                return

            current = self.coordinator.data.get("MBF_PAR_FILTRATION_CONF")
            if current is None or self._attr_mask is None or self._attr_shift is None:
                return

            new_val = (current & ~self._attr_mask) | (value << self._attr_shift)
            _LOGGER.debug(
                "Setting new filtration speed: current=0x%04X, new_val=0x%04X, mask=0x%04X, shift=%d",
                current,
                new_val,
                self._attr_mask,
                self._attr_shift,
            )
            await self.coordinator.client.async_write_register(
                self._register, new_val, apply=True
            )
            await asyncio.sleep(0.2)
            return

        value = None
        for k, v in self._options_map.items():
            if v == option:
                value = k
                break

        if value is not None:
            # Special: MBF_PAR_FILT_MODE needs to handle manual → other
            # We have to turn off manual filtration first (set register 0x0413 to 0)
            # and then set the new mode
            if self._key == "MBF_PAR_FILT_MODE":
                current_mode = self.coordinator.data.get(self._key)
                current_name = self._options_map.get(current_mode)
                if current_name == "manual" and option != "manual":
                    await self.coordinator.client.async_write_register(
                        MANUAL_FILTRATION_REGISTER, 0
                    )
                    await asyncio.sleep(0.1)
            # Set the new mode
            await self.coordinator.client.async_write_register(self._register, value)
            await asyncio.sleep(0.2)

        # Run a refresh to update the state
        await asyncio.sleep(0.5)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        _LOGGER.debug(
            "VistaPoolSelect ADDED: entity_id=%s, translation_key=%s, has_entity_name=%s",
            self.entity_id,
            self._attr_translation_key,
            getattr(self, "has_entity_name", None),
        )
        await super().async_added_to_hass()

    @property
    def options(self):
        option_keys = list(self._options_map.keys())

        # Hide heating and intelligent if not enabled heating mode
        if (
            self._key == "MBF_PAR_FILT_MODE"
            and self.coordinator.data.get("MBF_PAR_HEATING_MODE") == 0
        ):
            # Remove keys for "heating" and "intelligent"
            option_keys = [k for k in option_keys if k not in (2, 4)]

        # Hide smart if temperature sensor is not active
        if (
            self._key == "MBF_PAR_FILT_MODE"
            and self.coordinator.data.get("MBF_PAR_TEMPERATURE_ACTIVE") == 0
        ):
            # Remove key for "smart"
            option_keys = [k for k in option_keys if k != 3]

        # Add backwash option if enabled in config
        if (
            self._key == "MBF_PAR_FILT_MODE"
            and self.coordinator.config_entry.options.get(
                "enable_backwash_option", False
            )
        ):
            # Add backwash as the last option (key 13)
            if 13 not in option_keys:
                option_keys.append(13)
                self._options_map[13] = "backwash"
        else:
            # Remove key for "backwash" if it exists and not enabled
            option_keys = [k for k in option_keys if k != 13]

        # Hide "Active (Redox control)" if no Redox module
        if self._key == "MBF_CELL_BOOST" and not bool(
            self.coordinator.data.get("Redox measurement module detected")
        ):
            option_keys = [k for k in option_keys if k != 2]

        # Handle Timer options in cases where doesn't fit 15 minutes
        if self._select_type == "timer_time":
            value = self.coordinator.data.get(self._key)
            options_list = [self._options_map[k] for k in option_keys]
            if value is not None:
                current_hhmm = seconds_to_hhmm(value)
                if current_hhmm not in options_list:
                    return [current_hhmm] + options_list
            return options_list

        return [self._options_map[k] for k in option_keys]

    @property
    def current_option(self):
        if self._key == "MBF_CELL_BOOST":
            reg_val = self.coordinator.data.get(self._key)
            if reg_val is None:
                return None
            # 0: Inactive
            if reg_val == 0:
                return self._options_map[0]
            # 1: Active (redox control disabled) – bit 0x8000 set
            elif reg_val & 0x8000:
                return self._options_map[1]
            # 2: Active (Redox control) – bits 0x0500 | 0x00A0 set and 0x8000 NOT set
            elif (reg_val & (0x0500 | 0x00A0)) == (0x0500 | 0x00A0):
                return self._options_map[2]
            # fallback (should not occur)
            return self._options_map[0]

        if self._key == "MBF_PAR_FILTRATION_SPEED":
            raw = self.coordinator.data.get("MBF_PAR_FILTRATION_CONF")
            if raw is None:
                return None
            if self._attr_mask is None or self._attr_shift is None:
                return None
            value = (raw & self._attr_mask) >> self._attr_shift
            return self._options_map.get(value)

        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        if self._options_map:
            # If not exactly in options_map, always return current HH:MM
            return self._options_map.get(value) or seconds_to_hhmm(value)
        return seconds_to_hhmm(value)
