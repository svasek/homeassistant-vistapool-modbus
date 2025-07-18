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

import pytest
from unittest.mock import MagicMock, patch

from custom_components.vistapool import config_flow


@pytest.mark.asyncio
async def test_show_user_form_on_init():
    flow = config_flow.VistaPoolConfigFlow()
    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert "errors" in result
    # Check if the form schema contains host, port, slave_id, and name
    schema = result["data_schema"]
    assert "host" in str(schema)
    assert "port" in str(schema)


@pytest.mark.asyncio
async def test_create_entry_success():
    flow = config_flow.VistaPoolConfigFlow()
    user_input = {
        "host": "192.168.1.100",
        "port": 8899,
        "slave_id": 1,
        "name": "Test Pool",
    }
    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        return_value=True,
    ):
        result = await flow.async_step_user(user_input)
        assert result["type"] == "create_entry"
        assert result["title"] == "Test Pool"
        assert result["data"]["host"] == "192.168.1.100"
        assert result["data"]["port"] == 8899


@pytest.mark.asyncio
async def test_create_entry_failure():
    flow = config_flow.VistaPoolConfigFlow()
    user_input = {
        "host": "192.168.1.100",
        "port": 8899,
        "slave_id": 1,
        "name": "Test Pool",
    }
    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        return_value=False,
    ):
        result = await flow.async_step_user(user_input)
        assert result["type"] == "form"
        assert "host" in result["errors"]
        assert result["errors"]["host"] == "cannot_connect"
