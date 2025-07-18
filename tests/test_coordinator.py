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
from unittest.mock import MagicMock, AsyncMock, patch
from custom_components.vistapool.coordinator import VistaPoolCoordinator
from homeassistant.exceptions import ConfigEntryNotReady


@pytest.fixture
def mock_entry():
    entry = MagicMock()
    entry.options = {}
    entry.data = {"name": "Test Pool"}
    entry.entry_id = "entry_id_123"
    entry.unique_id = "test_slug"
    return entry


@pytest.mark.asyncio
async def test_async_update_data_success(mock_entry):
    client = AsyncMock()
    # Simulate async_read_all returns base dict
    client.async_read_all = AsyncMock(return_value={"MBF_POWER_MODULE_VERSION": 0x1234})
    client.read_all_timers = AsyncMock(return_value={})
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    data = await coordinator._async_update_data()
    assert "MBF_POWER_MODULE_VERSION" in data
    assert coordinator.firmware == "18.52"  # 0x1234 == 18.52
    assert coordinator.model == "VistaPool"


@pytest.mark.asyncio
async def test_async_update_data_uses_cached_on_error(mock_entry):
    client = AsyncMock()
    # First call to async_read_all will fail
    client.async_read_all = AsyncMock(side_effect=Exception("Modbus fail"))
    client.read_all_timers = AsyncMock()
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    coordinator.data = {"cached": "value"}
    with patch("custom_components.vistapool.coordinator._LOGGER"):
        data = await coordinator._async_update_data()
    assert data == {"cached": "value"}


@pytest.mark.asyncio
async def test_async_update_data_raises_ConfigEntryNotReady_on_first_error(mock_entry):
    client = AsyncMock()
    client.async_read_all = AsyncMock(side_effect=Exception("fail"))
    client.read_all_timers = AsyncMock()
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    # No .data attribute set, should raise
    with pytest.raises(ConfigEntryNotReady):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_async_update_data_time_sync(mock_entry):
    # auto_time_sync must be enabled, device time must be out of sync
    entry = MagicMock()
    entry.options = {"auto_time_sync": True}
    entry.data = {"name": "Test Pool"}
    entry.entry_id = "entry_id_321"
    entry.unique_id = "test_slug"
    client = AsyncMock()
    client.async_read_all = AsyncMock(return_value={"MBF_POWER_MODULE_VERSION": 0x2345})
    client.read_all_timers = AsyncMock(return_value={})
    client.async_write_register = AsyncMock()
    hass = MagicMock()
    with patch(
        "custom_components.vistapool.coordinator.is_device_time_out_of_sync",
        return_value=True,
    ), patch(
        "custom_components.vistapool.coordinator.prepare_device_time", return_value=1234
    ):
        coordinator = VistaPoolCoordinator(hass, client, entry, entry.entry_id)
        await coordinator._async_update_data()
    assert client.async_write_register.await_count == 2


@pytest.mark.asyncio
async def test_set_auto_time_sync(mock_entry):
    hass = MagicMock()
    hass.config_entries.async_update_entry = MagicMock()
    coordinator = VistaPoolCoordinator(
        hass, MagicMock(), mock_entry, mock_entry.entry_id
    )
    await coordinator.set_auto_time_sync(True)
    assert coordinator.auto_time_sync is True
    hass.config_entries.async_update_entry.assert_called_once()


def test_firmware_and_model_property(mock_entry):
    coordinator = VistaPoolCoordinator(
        MagicMock(), MagicMock(), mock_entry, mock_entry.entry_id
    )
    coordinator._firmware = "1.2"
    coordinator._model = "X"
    assert coordinator.firmware == "1.2"
    assert coordinator.model == "X"
    coordinator.device_name = "Pool"
    assert coordinator.device_name == "Pool"
