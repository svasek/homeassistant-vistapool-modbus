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
