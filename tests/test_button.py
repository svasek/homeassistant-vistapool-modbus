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
from custom_components.vistapool.button import VistaPoolButton


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
