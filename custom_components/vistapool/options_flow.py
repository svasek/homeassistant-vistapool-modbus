import logging
import asyncio
import voluptuous as vol
from datetime import date
from homeassistant import config_entries
from .entity import VistaPoolEntity
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class VistaPoolOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry
        self._base_options = {}

    async def async_step_init(self, user_input=None):
        # Get current options from the config entry
        options = dict(self._config_entry.options)
        already_enabled = options.get("enable_backwash_option", False)

        device_slug = VistaPoolEntity.slugify(self._config_entry.title)
        current_year = date.today().year
        expected = f"{device_slug}{current_year}"

        schema_dict = {
            vol.Optional(
                "scan_interval",
                default=options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
            ): int,
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

            if (
                prev_options.get("use_light") != user_input.get("use_light")
                or prev_options.get("use_aux1") != user_input.get("use_aux1")
                or prev_options.get("use_aux2") != user_input.get("use_aux2")
                or prev_options.get("use_aux3") != user_input.get("use_aux3")
                or prev_options.get("use_aux4") != user_input.get("use_aux4")
            ):
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

    async def async_step_advanced(self, user_input=None):
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
