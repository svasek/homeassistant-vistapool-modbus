# Copyright 2025 Miloš Svašek

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""VistaPool Integration for Home Assistant - Config Flow"""

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
                vol.Optional("slave_id", default=DEFAULT_SLAVE_ID): int,
                vol.Optional(
                    "scan_interval",
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.In([5, 10, 15, 20, 30, 45, 60, 120, 180, 300]),
                vol.Optional(
                    "use_filtration1",
                    default=True,
                ): bool,
                vol.Optional(
                    "use_filtration2",
                    default=False,
                ): bool,
                vol.Optional(
                    "use_filtration3",
                    default=False,
                ): bool,
                vol.Optional(
                    "use_light",
                    default=False,
                ): bool,
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

    @staticmethod
    def async_get_options_flow(config_entry):
        from .options_flow import VistaPoolOptionsFlowHandler

        return VistaPoolOptionsFlowHandler(config_entry)
