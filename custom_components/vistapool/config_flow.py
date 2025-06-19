import asyncio
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SLAVE_ID, DEFAULT_SCAN_INTERVAL


async def is_host_port_open(host, port, timeout=3):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


class VistaPoolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VistaPool."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> dict | None:
        """Handle the initial step of the configuration flow."""
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DOMAIN.capitalize()): str,
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
                vol.Optional(
                    "scan_interval",
                    ("scan_interval", DEFAULT_SCAN_INTERVAL),
                ): vol.In([5, 10, 15, 20, 30, 45, 60, 120, 180, 300]),
                vol.Optional("slave_id", default=DEFAULT_SLAVE_ID): int,
            }
        )
        errors = {}
        if user_input is not None:
            device_name = user_input.get(CONF_NAME, DOMAIN)
            user_input[CONF_NAME] = device_name

            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            if not await is_host_port_open(host, port):
                errors[CONF_HOST] = "cannot_connect"
            if errors:
                # Keep the previously entered values except for required fields
                return self.async_show_form(
                    step_id="user",
                    data_schema=data_schema,
                    errors=errors,
                )
            return self.async_create_entry(title=device_name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    def async_get_options_flow(config_entry):
        from .options_flow import VistaPoolOptionsFlowHandler

        return VistaPoolOptionsFlowHandler(config_entry)
