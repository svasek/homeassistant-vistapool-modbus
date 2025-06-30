import logging
import asyncio
import voluptuous as vol
from datetime import date
from homeassistant import config_entries
from homeassistant.util import slugify
from .entity import VistaPoolEntity
from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_TIMER_RESOLUTION

_LOGGER = logging.getLogger(__name__)


class VistaPoolOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for VistaPool integration."""

    def __init__(self, config_entry) -> None:
        """Initialize the options flow handler."""
        super().__init__()
        self._config_entry = config_entry
        self._base_options = {}

    async def async_step_init(self, user_input=None) -> dict:
        """Handle the initial step of the options flow."""
        # Get current options from the config entry
        options = dict(self._config_entry.options)
        already_enabled = options.get("enable_backwash_option", False)

        device_slug = self.config_entry.unique_id or slugify(
            self.config_entry.data.get("name")
        )
        expected = f"{device_slug}{date.today().year}"

        schema_dict = {
            vol.Optional(
                "scan_interval",
                default=options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
            ): vol.In([5, 10, 15, 20, 30, 45, 60, 120, 180, 300]),
            vol.Optional(
                "timer_resolution",
                default=options.get("timer_resolution", DEFAULT_TIMER_RESOLUTION),
            ): vol.In([1, 5, 10, 15, 30, 60]),
            vol.Optional(
                "measure_when_filtration_off",
                default=options.get("measure_when_filtration_off", False),
            ): bool,
            vol.Optional(
                "use_filtration1",
                default=options.get("use_filtration1", True),
            ): bool,
            vol.Optional(
                "use_filtration2",
                default=options.get("use_filtration2", False),
            ): bool,
            vol.Optional(
                "use_filtration3",
                default=options.get("use_filtration3", False),
            ): bool,
            vol.Optional(
                "use_light",
                default=options.get("use_light", False),
            ): bool,
            vol.Optional(
                "use_aux1",
                default=options.get("use_aux1", False),
            ): bool,
            vol.Optional(
                "use_aux2",
                default=options.get("use_aux2", False),
            ): bool,
            vol.Optional(
                "use_aux3",
                default=options.get("use_aux3", False),
            ): bool,
            vol.Optional(
                "use_aux4",
                default=options.get("use_aux4", False),
            ): bool,
        }

        if already_enabled:
            schema_dict[
                vol.Optional(
                    "enable_backwash_option",
                    default=True,
                    description={"suggested_value": True},
                )
            ] = bool
        else:
            schema_dict[vol.Optional("unlock_advanced", default="")] = str

        schema = vol.Schema(schema_dict)

        if user_input is not None:
            if already_enabled:
                return self.async_create_entry(title="", data=user_input)
            if (user_input.get("unlock_advanced") or "").strip() == expected:
                self._base_options = user_input.copy()
                self._base_options.pop("unlock_advanced", None)
                return await self.async_step_advanced()
            else:
                if (user_input.get("unlock_advanced") or "").strip() != "":
                    _LOGGER.warning("Wrong password for the advanced settings!")
                    return self.async_show_form(
                        step_id="init",
                        data_schema=schema,
                        errors={"unlock_advanced": "unlock_advanced_error"},
                    )
            data = user_input.copy()
            data.pop("unlock_advanced", None)
            prev_options = dict(self._config_entry.options)
            result = self.async_create_entry(title="", data=data)

            # Dynamically collect all 'use_*' option keys to compare changes and trigger reload if needed
            reload_keys = sorted(
                {
                    k
                    for k in list(prev_options) + list(user_input)
                    if k.startswith("use_")
                }
            )
            if any(prev_options.get(k) != user_input.get(k) for k in reload_keys):
                self.hass.loop.call_soon(
                    asyncio.create_task,
                    self.hass.config_entries.async_reload(self._config_entry.entry_id),
                )

            return result

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={},
        )

    async def async_step_advanced(self, user_input=None) -> dict:
        """Handle the advanced options step."""
        options = dict(self._config_entry.options)
        advanced_schema = vol.Schema(
            {
                vol.Optional(
                    "enable_backwash_option",
                    default=options.get("enable_backwash_option", False),
                ): bool,
            }
        )

        if user_input is not None:
            prev_options = dict(self._config_entry.options)
            all_options = {**self._base_options, **user_input}
            result = self.async_create_entry(title="", data=all_options)

            if (
                prev_options.get("use_light") != all_options.get("use_light")
                or prev_options.get("use_aux1") != all_options.get("use_aux1")
                or prev_options.get("use_aux2") != all_options.get("use_aux2")
                or prev_options.get("use_aux3") != all_options.get("use_aux3")
                or prev_options.get("use_aux4") != all_options.get("use_aux4")
            ):
                self.hass.loop.call_soon(
                    asyncio.create_task,
                    self.hass.config_entries.async_reload(self._config_entry.entry_id),
                )

            return result

        return self.async_show_form(
            step_id="advanced",
            data_schema=advanced_schema,
            description_placeholders={
                "warning": (
                    "WARNING: Enabling backwash will add this mode to Filtration Mode select. "
                    "Improper use may damage the filter! Enable only if you know what you are doing."
                )
            },
            last_step=True,
        )
