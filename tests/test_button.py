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
from unittest.mock import MagicMock, AsyncMock
from custom_components.vistapool.button import VistaPoolButton, async_setup_entry


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    mock.client = AsyncMock()
    mock.async_request_refresh = AsyncMock()
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.unique_id = "test_slug"
    mock.config_entry = config_entry
    return mock


@pytest.fixture
def button_props():
    return {"icon": "mdi:button-pointer"}


def test_button_attrs(mock_coordinator, button_props):
    ent = VistaPoolButton(mock_coordinator, "test_entry", "SYNC_TIME", button_props)
    assert ent._key == "SYNC_TIME"
    assert ent.icon == "mdi:button-pointer"


@pytest.mark.asyncio
async def test_button_press_sync_time(mock_coordinator, button_props):
    ent = VistaPoolButton(mock_coordinator, "test_entry", "SYNC_TIME", button_props)
    ent.hass = MagicMock()
    ent.hass.config = MagicMock()
    ent.hass.config.time_zone = "Europe/Prague"
    await ent.async_press()
    assert mock_coordinator.client.async_write_register.called


@pytest.mark.asyncio
async def test_button_press_escape(mock_coordinator, button_props):
    """Test async_press calls correct register writes for MBF_ESCAPE button."""
    ent = VistaPoolButton(mock_coordinator, "test_entry", "MBF_ESCAPE", button_props)
    ent.hass = MagicMock()
    await ent.async_press()
    # Should write to 0x0297, value 1
    mock_coordinator.client.async_write_register.assert_any_await(0x0297, 1)
    mock_coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_button_async_setup_entry_adds_entities(monkeypatch):
    """Test async_setup_entry adds button entities for all definitions."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {"something": True}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()
    # Patch BUTTON_DEFINITIONS
    from custom_components.vistapool import button as btn_module

    btn_module.BUTTON_DEFINITIONS["TEST_BUTTON"] = {"icon": "mdi:test"}
    await async_setup_entry(hass, entry, async_add_entities)
    # Should add entity for each key in BUTTON_DEFINITIONS
    entities = async_add_entities.call_args[0][0]
    assert any(isinstance(e, VistaPoolButton) for e in entities)
    assert any(e._key == "TEST_BUTTON" for e in entities)


@pytest.mark.asyncio
async def test_button_async_setup_entry_no_data(monkeypatch, caplog):
    """Test async_setup_entry logs warning and adds no entities when no data."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    with caplog.at_level("WARNING"):
        await async_setup_entry(hass, entry, async_add_entities)
        assert "No data from Modbus" in caplog.text
    async_add_entities.assert_not_called()
