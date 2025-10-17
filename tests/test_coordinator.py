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


@pytest.mark.asyncio
async def test_async_update_data_timer_processing(mock_entry):
    # Prepare a fake timer block with different value combinations
    client = AsyncMock()
    client.async_read_all = AsyncMock(return_value={"MBF_POWER_MODULE_VERSION": 0x1234})
    # Simulate two timers: one with both 'on' and 'interval', another with 'on' missing
    client.read_all_timers = AsyncMock(
        return_value={
            "filtration1": {
                "enable": True,
                "on": 1000,  # e.g. 1000 seconds since midnight
                "interval": 3600,  # 1 hour
                "period": 2,
            },
            "filtration2": {
                "enable": False,
                "on": None,
                "interval": 1800,  # 30 minutes
                "period": 1,
            },
        }
    )
    # Set options so at least one timer will be enabled
    entry = MagicMock()
    entry.options = {"use_filtration1": True, "use_filtration2": True}
    entry.data = {"name": "Test Pool"}
    entry.entry_id = "test_entry_id"
    entry.unique_id = "test_slug"

    coordinator = VistaPoolCoordinator(MagicMock(), client, entry, entry.entry_id)
    data = await coordinator._async_update_data()

    # Check that timer data keys are present and correctly computed
    assert data["filtration1_enable"] is True
    assert data["filtration1_start"] == 1000
    assert data["filtration1_interval"] == 3600
    assert data["filtration1_period"] == 2
    # stop = (1000 + 3600) % 86400 = 4600
    assert data["filtration1_stop"] == 4600

    assert data["filtration2_enable"] is False
    assert data["filtration2_start"] is None
    assert data["filtration2_interval"] == 1800
    assert data["filtration2_period"] == 1
    assert data["filtration2_stop"] is None


@pytest.mark.asyncio
async def test_setpoint_sync_on_mismatch(mock_entry):
    client = AsyncMock()
    # Return differing setpoints to trigger sync
    client.async_read_all = AsyncMock(
        return_value={
            "MBF_POWER_MODULE_VERSION": 0x1234,
            "MBF_PAR_HEATING_TEMP": 28,
            "MBF_PAR_INTELLIGENT_TEMP": 26,
        }
    )
    client.read_all_timers = AsyncMock(return_value={})
    client.async_write_register = AsyncMock()
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    # Seed previous snapshot so only HEATING changed this cycle
    coordinator.data = {
        "MBF_PAR_HEATING_TEMP": 27,
        "MBF_PAR_INTELLIGENT_TEMP": 26,
    }
    data = await coordinator._async_update_data()
    # Coordinator should sync only the unaffected register (INTELLIGENT) to the new HEATING value
    assert client.async_write_register.await_count == 1
    call_args = client.async_write_register.await_args_list[0]
    # Address and value
    assert call_args[0][0] == 0x041C  # INTELLIGENT_SETPOINT_REGISTER
    assert call_args[0][1] == 28
    # apply should be True for the syncing write
    assert call_args[1].get("apply", False) is True
    # Returned data should reflect synced values
    assert data["MBF_PAR_HEATING_TEMP"] == 28
    assert data["MBF_PAR_INTELLIGENT_TEMP"] == 28


@pytest.mark.asyncio
async def test_setpoint_sync_on_mismatch_intel_changed(mock_entry):
    client = AsyncMock()
    # Return differing setpoints to trigger sync
    client.async_read_all = AsyncMock(
        return_value={
            "MBF_POWER_MODULE_VERSION": 0x1234,
            "MBF_PAR_HEATING_TEMP": 26,
            "MBF_PAR_INTELLIGENT_TEMP": 28,
        }
    )
    client.read_all_timers = AsyncMock(return_value={})
    client.async_write_register = AsyncMock()
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    # Seed previous snapshot so only INTELLIGENT changed this cycle
    coordinator.data = {
        "MBF_PAR_HEATING_TEMP": 26,
        "MBF_PAR_INTELLIGENT_TEMP": 27,
    }
    data = await coordinator._async_update_data()
    # Coordinator should sync only the unaffected register (HEATING) to the new INTELLIGENT value
    assert client.async_write_register.await_count == 1
    call_args = client.async_write_register.await_args_list[0]
    assert call_args[0][0] == 0x0416  # HEATING_SETPOINT_REGISTER
    assert call_args[0][1] == 28
    assert call_args[1].get("apply", False) is True
    assert data["MBF_PAR_HEATING_TEMP"] == 28
    assert data["MBF_PAR_INTELLIGENT_TEMP"] == 28


@pytest.mark.asyncio
async def test_setpoint_sync_both_changed_conflict(mock_entry):
    client = AsyncMock()
    # Both changed to different values in this cycle
    client.async_read_all = AsyncMock(
        return_value={
            "MBF_POWER_MODULE_VERSION": 0x1234,
            "MBF_PAR_HEATING_TEMP": 28,
            "MBF_PAR_INTELLIGENT_TEMP": 26,
        }
    )
    client.read_all_timers = AsyncMock(return_value={})
    client.async_write_register = AsyncMock()
    coordinator = VistaPoolCoordinator(
        MagicMock(), client, mock_entry, mock_entry.entry_id
    )
    # Previous snapshot with different values so that both appear changed now
    coordinator.data = {
        "MBF_PAR_HEATING_TEMP": 27,
        "MBF_PAR_INTELLIGENT_TEMP": 27,
    }
    data = await coordinator._async_update_data()
    # No write should occur when both changed differently (to avoid overriding intent)
    assert client.async_write_register.await_count == 0
    # Data should remain as read (no forced unification)
    assert data["MBF_PAR_HEATING_TEMP"] == 28
    assert data["MBF_PAR_INTELLIGENT_TEMP"] == 26


@pytest.mark.asyncio
async def test_dev_overrides_applied_valid_json(mock_entry):
    # Enable overrides with valid JSON string
    entry = MagicMock()
    entry.options = {
        "dev_overrides_enabled": True,
        "dev_overrides": '{"MBF_PAR_CLIMA_ONOFF": 1, "MBF_PAR_MODEL": 1}',
    }
    entry.data = {"name": "Test Pool"}
    entry.entry_id = "entry_id_dev1"
    entry.unique_id = "test_slug"

    client = AsyncMock()
    client.async_read_all = AsyncMock(
        return_value={
            "MBF_POWER_MODULE_VERSION": 0x1234,
            "MBF_PAR_CLIMA_ONOFF": 0,
        }
    )
    client.read_all_timers = AsyncMock(return_value={})

    coordinator = VistaPoolCoordinator(MagicMock(), client, entry, entry.entry_id)
    data = await coordinator._async_update_data()

    # Overrides should be applied over the base read values
    assert data["MBF_PAR_CLIMA_ONOFF"] == 1
    assert data["MBF_PAR_MODEL"] == 1


@pytest.mark.asyncio
async def test_dev_overrides_invalid_json_ignored(mock_entry):
    entry = MagicMock()
    entry.options = {
        "dev_overrides_enabled": True,
        "dev_overrides": "this-is-not-json",
    }
    entry.data = {"name": "Test Pool"}
    entry.entry_id = "entry_id_dev2"
    entry.unique_id = "test_slug"

    client = AsyncMock()
    client.async_read_all = AsyncMock(return_value={"X": 1})
    client.read_all_timers = AsyncMock(return_value={})

    with patch("custom_components.vistapool.coordinator._LOGGER") as mock_logger:
        coordinator = VistaPoolCoordinator(MagicMock(), client, entry, entry.entry_id)
        data = await coordinator._async_update_data()
        # Should log a warning about failed overrides but not raise
        assert mock_logger.warning.called

    # Data remains as originally read (no overrides applied)
    assert data.get("X") == 1
    assert "MBF_PAR_CLIMA_ONOFF" not in data
    assert "MBF_PAR_MODEL" not in data
