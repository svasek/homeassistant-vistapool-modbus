import voluptuous as vol
from homeassistant import config_entries
from .const import DEFAULT_SCAN_INTERVAL


class VistaPoolOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self._config_entry.options.get(
                            "scan_interval", DEFAULT_SCAN_INTERVAL
                        ),
                    ): int,
                    vol.Optional(
                        "use_light",
                        default=self._config_entry.options.get("use_light", False),
                    ): bool,
                    vol.Optional(
                        "use_aux1",
                        default=self._config_entry.options.get("use_aux1", False),
                    ): bool,
                    vol.Optional(
                        "use_aux2",
                        default=self._config_entry.options.get("use_aux2", False),
                    ): bool,
                    vol.Optional(
                        "use_aux3",
                        default=self._config_entry.options.get("use_aux3", False),
                    ): bool,
                    vol.Optional(
                        "use_aux4",
                        default=self._config_entry.options.get("use_aux4", False),
                    ): bool,
                }
            ),
        )
