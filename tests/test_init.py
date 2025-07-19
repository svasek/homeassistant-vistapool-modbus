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
from custom_components.vistapool import (
    async_setup_entry,
    async_unload_entry,
    async_setup,
)


@pytest.mark.asyncio
async def test_async_handle_set_timer_happy(monkeypatch):
    """Test async_handle_set_timer sets timer correctly with all parameters."""

    hass = MagicMock()
    hass.data = {"vistapool": {"entry1": MagicMock()}}
    coordinator = hass.data["vistapool"]["entry1"]
    coordinator.client.write_timer = AsyncMock(return_value=True)
    coordinator.async_request_refresh = AsyncMock()

    # Prepare call mock
    call = MagicMock()
    call.data = {
        "timer": "filtration1",
        "start": "08:30",
        "stop": "10:15",
        "enable": 1,
        "entry_id": "entry1",
        "period": 1234,
    }

    # Register service and extract handler
    await async_setup(hass, {})
    service_func = hass.services.async_register.call_args[0][2]

    await service_func(call)

    # Check correct timer data sent to write_timer
    coordinator.client.write_timer.assert_awaited_once_with(
        "filtration1",
        {"on": 30600, "interval": 6300, "period": 1234, "enable": 1},
    )
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_handle_set_timer_entry_id_fallback(monkeypatch):
    """Test async_handle_set_timer uses fallback entry_id if not provided."""

    hass = MagicMock()
    hass.data = {"vistapool": {"fallback": MagicMock()}}
    coordinator = hass.data["vistapool"]["fallback"]
    coordinator.client.write_timer = AsyncMock(return_value=True)
    coordinator.async_request_refresh = AsyncMock()

    call = MagicMock()
    call.data = {
        "timer": "relay_aux1",
        "start": "00:00",
        "stop": "01:00",
        "enable": 0,
        # "entry_id" intentionally missing!
    }

    await async_setup(hass, {})
    service_func = hass.services.async_register.call_args[0][2]
    await service_func(call)

    coordinator.client.write_timer.assert_awaited_once_with(
        "relay_aux1",
        {"on": 0, "interval": 3600, "enable": 0},
    )


from homeassistant.exceptions import ServiceValidationError


@pytest.mark.asyncio
async def test_async_handle_set_timer_missing_entry(monkeypatch):
    """Test async_handle_set_timer raises ServiceValidationError if no entry_id found."""

    hass = MagicMock()
    hass.data = {"vistapool": {}}
    call = MagicMock()
    call.data = {
        "timer": "relay_aux2",
        "start": "12:00",
        "stop": "13:00",
        # no entry_id, and no fallback available
    }

    await async_setup(hass, {})
    service_func = hass.services.async_register.call_args[0][2]
    with pytest.raises(ServiceValidationError):
        await service_func(call)


@pytest.mark.asyncio
async def test_async_handle_set_timer_write_timer_exception(monkeypatch):
    """Test async_handle_set_timer raises ServiceValidationError on write_timer exception."""

    hass = MagicMock()
    hass.data = {"vistapool": {"entryX": MagicMock()}}
    coordinator = hass.data["vistapool"]["entryX"]
    coordinator.client.write_timer = AsyncMock(side_effect=Exception("fail!"))
    coordinator.async_request_refresh = AsyncMock()

    call = MagicMock()
    call.data = {
        "timer": "relay_aux2",
        "start": "14:00",
        "stop": "14:30",
        "entry_id": "entryX",
    }

    await async_setup(hass, {})
    service_func = hass.services.async_register.call_args[0][2]
    with pytest.raises(ServiceValidationError):
        await service_func(call)


@pytest.mark.asyncio
async def test_async_setup_entry_success():
    """Test async_setup_entry completes successfully."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)
    config_entry = MagicMock()
    with patch("custom_components.vistapool.VistaPoolModbusClient"):
        with patch(
            "custom_components.vistapool.VistaPoolCoordinator"
        ) as mock_coordinator:
            mock_coord_instance = mock_coordinator.return_value
            mock_coord_instance.async_config_entry_first_refresh = AsyncMock(
                return_value=None
            )
            result = await async_setup_entry(hass, config_entry)
            assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_success():
    """Test async_unload_entry completes successfully."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    config_entry = MagicMock()
    config_entry.entry_id = "entry1"
    # Simulate coordinator with client in hass.data
    coordinator = MagicMock()
    coordinator.client = AsyncMock()
    hass.data = {"vistapool": {"entry1": coordinator}}
    hass.services.async_remove = MagicMock()
    result = await async_unload_entry(hass, config_entry)
    assert result is True
    # Check that client.close() was called
    assert coordinator.client.close.await_count == 1


@pytest.mark.asyncio
async def test_async_unload_entry_no_coordinator():
    """Test async_unload_entry when coordinator is missing."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    config_entry = MagicMock()
    config_entry.entry_id = "entryX"
    hass.data = {"vistapool": {}}
    hass.services.async_remove = MagicMock()
    result = await async_unload_entry(hass, config_entry)
    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_no_client():
    """Test async_unload_entry when coordinator has no client."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    config_entry = MagicMock()
    config_entry.entry_id = "entry2"
    coordinator = MagicMock()
    coordinator.client = None
    hass.data = {"vistapool": {"entry2": coordinator}}
    hass.services.async_remove = MagicMock()
    result = await async_unload_entry(hass, config_entry)
    assert result is True


@pytest.mark.asyncio
async def test_async_setup_registers_service():
    """Test async_setup registers the sync_time service."""
    hass = MagicMock()
    hass.services.async_register = MagicMock()
    result = await async_setup(hass, {})
    assert result is True
    hass.services.async_register.assert_called_once()
