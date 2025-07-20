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
from custom_components.vistapool.diagnostics import async_get_config_entry_diagnostics


@pytest.mark.asyncio
async def test_async_get_config_entry_diagnostics_filters_sensitive_data():
    # Prepare a mock config_entry with sensitive data
    entry = MagicMock()
    entry.data = {
        "host": "192.168.1.100",
        "port": 8899,
        "password": "secret",
        "apitoken": "abcdef",
        "user": "admin",
    }
    entry.options = {"option1": True}
    entry.title = "Test Pool"
    entry.entry_id = "entry1"
    entry.version = 1

    # Prepare a mock client
    client = MagicMock()
    client.connection_stats = {
        "retries": 3,
        "host": "192.168.1.100",
        "port": 8899,
        "unit_id": 1,
        "connected": True,
    }

    # Prepare a mock coordinator
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.last_update_time = "2025-07-19 10:00:00"
    coordinator.data = {"some": "data"}
    coordinator.update_interval = 60
    coordinator.last_exception = None
    coordinator.firmware = "1.0"
    coordinator.model = "Vistapool"
    coordinator.client = client

    # Prepare a mock hass object with the coordinator registered
    hass = MagicMock()
    hass.data = {"vistapool": {"entry1": coordinator}}

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    # Ensure password and apitoken are filtered out from the result
    data_keys = diagnostics["config_entry"]["data"].keys()
    assert "password" not in data_keys
    assert "apitoken" not in data_keys
    assert "user" in data_keys

    # Ensure all sections are present and have correct values
    assert diagnostics["config_entry"]["title"] == "Test Pool"
    assert diagnostics["config_entry"]["entry_id"] == "entry1"
    assert diagnostics["coordinator"]["firmware"] == "1.0"
    assert diagnostics["coordinator"]["model"] == "Vistapool"
    assert diagnostics["connection_stats"]["retries"] == 3


@pytest.mark.asyncio
async def test_diagnostics_without_coordinator_returns_empty():
    # Prepare a mock config_entry without a matching coordinator in hass.data
    entry = MagicMock()
    entry.entry_id = "entry42"
    hass = MagicMock()
    hass.data = {"vistapool": {}}

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    # If no coordinator is found, diagnostics should be minimal
    assert diagnostics["config_entry"]["entry_id"] == "entry42"
    assert "coordinator" not in diagnostics or diagnostics["coordinator"] is None


@pytest.mark.asyncio
async def test_diagnostics_with_coordinator_but_no_client():
    # Prepare a mock config_entry with a coordinator that has no client
    entry = MagicMock()
    entry.entry_id = "entry1"
    hass = MagicMock()
    coordinator = MagicMock()
    coordinator.client = None  # Simulate missing client
    hass.data = {"vistapool": {"entry1": coordinator}}

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    # Diagnostics should not fail if client is None
    assert diagnostics["config_entry"]["entry_id"] == "entry1"
    assert "client" not in diagnostics or diagnostics["client"] is None


@pytest.mark.asyncio
async def test_diagnostics_with_coordinator_with_partial_attributes():
    # Prepare a mock config_entry with coordinator missing some attributes
    entry = MagicMock()
    entry.entry_id = "entry1"
    hass = MagicMock()
    coordinator = MagicMock()
    # Only set data and client, omit other attributes
    coordinator.data = {"key": "value"}
    coordinator.client = MagicMock()
    hass.data = {"vistapool": {"entry1": coordinator}}

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    # Ensure diagnostics still contain available attributes
    assert diagnostics["coordinator"]["data"] == {"key": "value"}
    assert "connection_stats" in diagnostics
