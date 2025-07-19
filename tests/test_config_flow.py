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
from unittest.mock import AsyncMock, MagicMock, patch

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


def test_async_get_options_flow(monkeypatch):
    class DummyConfigEntry:
        pass

    class DummyOptionsFlow:
        def __init__(self, config_entry):
            self.called = True
            self.config_entry = config_entry

    # Patch import ve funkci
    monkeypatch.setattr(
        "custom_components.vistapool.options_flow.VistaPoolOptionsFlowHandler",
        DummyOptionsFlow,
    )
    config_entry = DummyConfigEntry()
    handler = config_flow.VistaPoolConfigFlow.async_get_options_flow(config_entry)
    assert isinstance(handler, DummyOptionsFlow)
    assert handler.config_entry is config_entry


@pytest.mark.asyncio
async def test_is_host_port_open_exception():
    # Monkeypatch asyncio.open_connection to raise
    async def raise_exc(*args, **kwargs):
        raise OSError("fail")

    monkeypatch = patch("asyncio.open_connection", raise_exc)
    with monkeypatch:
        result = await config_flow.is_host_port_open("127.0.0.1", 9999)
        assert result is False


@pytest.mark.asyncio
async def test_is_host_port_open_success(monkeypatch):
    reader = MagicMock()
    writer = MagicMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()

    async def fake_open_connection(host, port):
        return reader, writer

    monkeypatch.setattr("asyncio.open_connection", fake_open_connection)
    result = await config_flow.is_host_port_open("127.0.0.1", 502)
    writer.close.assert_called_once()
    writer.wait_closed.assert_awaited_once()
    assert result is True
