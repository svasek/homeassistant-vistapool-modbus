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
from custom_components.vistapool.const import DEFAULT_PORT


@pytest.mark.asyncio
async def test_show_user_form_on_init():
    flow = config_flow.VistaPoolConfigFlow()
    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert "errors" in result
    # Check if the form schema contains host, port, slave_id, name and modbus_framer
    schema = result["data_schema"]
    assert "host" in str(schema)
    assert "port" in str(schema)
    assert "slave_id" in str(schema)
    assert "name" in str(schema)
    assert "modbus_framer" in str(schema)


@pytest.mark.asyncio
async def test_create_entry_success():
    flow = config_flow.VistaPoolConfigFlow()
    user_input = {
        "host": "192.168.1.100",
        "port": DEFAULT_PORT,
        "slave_id": 1,
        "name": "Test Pool",
    }
    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        new=AsyncMock(return_value=True),
    ):
        result = await flow.async_step_user(user_input)
        assert result["type"] == "create_entry"
        assert result["title"] == "Test Pool"
        assert result["data"]["host"] == "192.168.1.100"
        assert result["data"]["port"] == DEFAULT_PORT


@pytest.mark.asyncio
async def test_create_entry_with_rtu_framer():
    """Test that modbus_framer='rtu' is accepted and stored in config entry."""
    flow = config_flow.VistaPoolConfigFlow()
    user_input = {
        "host": "192.168.1.100",
        "port": DEFAULT_PORT,
        "slave_id": 1,
        "name": "Test Pool RTU",
        "modbus_framer": "rtu",
    }
    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        new=AsyncMock(return_value=True),
    ):
        result = await flow.async_step_user(user_input)
        assert result["type"] == "create_entry"
        assert result["data"]["modbus_framer"] == "rtu"


@pytest.mark.asyncio
async def test_create_entry_failure():
    flow = config_flow.VistaPoolConfigFlow()
    user_input = {
        "host": "192.168.1.100",
        "port": DEFAULT_PORT,
        "slave_id": 1,
        "name": "Test Pool",
    }
    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        new=AsyncMock(return_value=False),
    ):
        result = await flow.async_step_user(user_input)
        assert result["type"] == "form"
        assert "host" in result["errors"]
        assert result["errors"]["host"] == "cannot_connect"


def test_async_get_options_flow(monkeypatch):
    class DummyConfigEntry:
        pass

    class DummyOptionsFlow:
        """Mirrors the new OptionsFlow API: no config_entry injected via __init__."""

        def __init__(self):
            self.called = True

    # Patch import ve funkci
    monkeypatch.setattr(
        "custom_components.vistapool.options_flow.VistaPoolOptionsFlowHandler",
        DummyOptionsFlow,
    )
    config_entry = DummyConfigEntry()
    handler = config_flow.VistaPoolConfigFlow.async_get_options_flow(config_entry)
    assert isinstance(handler, DummyOptionsFlow)
    assert handler.called is True


@pytest.mark.asyncio
async def test_reconfigure_shows_form_with_current_data():
    """Reconfigure form is shown with pre-filled values from the existing entry."""
    flow = config_flow.VistaPoolConfigFlow()

    existing_data = {
        "host": "10.0.0.1",
        "port": 502,
        "slave_id": 2,
        "modbus_framer": "rtu",
        "name": "MyPool",
        "scan_interval": 30,
    }
    mock_entry = MagicMock()
    mock_entry.data = existing_data

    flow.hass = MagicMock()
    flow.hass.config_entries.async_get_entry.return_value = mock_entry
    flow.context = {"entry_id": "abc123"}

    result = await flow.async_step_reconfigure(user_input=None)

    assert result["type"] == "form"
    assert result["step_id"] == "reconfigure"
    assert not result.get("errors")
    schema_str = str(result["data_schema"])
    assert "host" in schema_str
    assert "port" in schema_str
    assert "slave_id" in schema_str
    assert "modbus_framer" in schema_str


@pytest.mark.asyncio
async def test_reconfigure_success():
    """Successful reconfiguration merges new values and calls update_reload_and_abort."""
    flow = config_flow.VistaPoolConfigFlow()

    existing_data = {
        "host": "10.0.0.1",
        "port": 502,
        "slave_id": 1,
        "modbus_framer": "tcp",
        "name": "MyPool",
        "scan_interval": 30,
    }
    mock_entry = MagicMock()
    mock_entry.data = existing_data

    flow.hass = MagicMock()
    flow.hass.config_entries.async_get_entry.return_value = mock_entry
    flow.context = {"entry_id": "abc123"}
    flow._get_reconfigure_entry = MagicMock(return_value=mock_entry)
    flow.async_update_reload_and_abort = MagicMock(
        return_value={"type": "abort", "reason": "reconfigure_successful"}
    )

    user_input = {
        "host": "10.0.0.99",
        "port": 503,
        "slave_id": 2,
        "modbus_framer": "rtu",
    }

    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        new=AsyncMock(return_value=True),
    ):
        result = await flow.async_step_reconfigure(user_input)

    assert result["type"] == "abort"
    assert result["reason"] == "reconfigure_successful"

    call_kwargs = flow.async_update_reload_and_abort.call_args
    saved_data = call_kwargs[1]["data"]
    # New values overwrite old ones
    assert saved_data["host"] == "10.0.0.99"
    assert saved_data["port"] == 503
    assert saved_data["slave_id"] == 2
    assert saved_data["modbus_framer"] == "rtu"
    # Unchanged values from original entry are preserved
    assert saved_data["name"] == "MyPool"
    assert saved_data["scan_interval"] == 30


@pytest.mark.asyncio
async def test_reconfigure_cannot_connect():
    """Reconfigure shows cannot_connect error when host is unreachable."""
    flow = config_flow.VistaPoolConfigFlow()

    mock_entry = MagicMock()
    mock_entry.data = {
        "host": "10.0.0.1",
        "port": 502,
        "slave_id": 1,
        "modbus_framer": "tcp",
    }

    flow.hass = MagicMock()
    flow.hass.config_entries.async_get_entry.return_value = mock_entry
    flow.context = {"entry_id": "abc123"}

    user_input = {
        "host": "10.0.0.99",
        "port": 502,
        "slave_id": 1,
        "modbus_framer": "tcp",
    }

    with patch(
        "custom_components.vistapool.config_flow.is_host_port_open",
        new=AsyncMock(return_value=False),
    ):
        result = await flow.async_step_reconfigure(user_input)

    assert result["type"] == "form"
    assert result["step_id"] == "reconfigure"
    assert result["errors"].get("host") == "cannot_connect"


@pytest.mark.asyncio
async def test_reconfigure_entry_not_found_aborts():
    """When the entry cannot be found, the flow aborts gracefully."""
    flow = config_flow.VistaPoolConfigFlow()

    flow.hass = MagicMock()
    flow.hass.config_entries.async_get_entry.return_value = None
    flow.context = {"entry_id": "missing"}
    flow.async_abort = MagicMock(return_value={"type": "abort", "reason": "entry_not_found"})

    result = await flow.async_step_reconfigure(user_input=None)

    assert result["type"] == "abort"
    assert result["reason"] == "entry_not_found"


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
    result = await config_flow.is_host_port_open("127.0.0.1", DEFAULT_PORT)
    writer.close.assert_called_once()
    writer.wait_closed.assert_awaited_once()
    assert result is True
