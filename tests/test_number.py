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
from custom_components.vistapool.number import VistaPoolNumber


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    mock.config_entry.entry_id = "test_entry"
    return mock


def make_props(**kwargs):
    d = {}
    d.update(kwargs)
    return d


def test_native_value_default(mock_coordinator):
    props = make_props(register=0x0200, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    mock_coordinator.data = {"MBF_PAR_PH1": 7.22}
    assert ent.native_value == 7.22


def test_native_value_none(mock_coordinator):
    props = make_props(register=0x0200, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    mock_coordinator.data = {}
    ent._attr_native_value = 7.01
    assert ent.native_value == 7.01


def test_suggested_display_precision(mock_coordinator):
    props = make_props()
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_HIDRO", props)
    assert ent.suggested_display_precision == 0
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_HEATING_TEMP", props)
    assert ent.suggested_display_precision == 0
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    assert ent.suggested_display_precision is None


def test_native_unit_of_measurement_dynamic(mock_coordinator):
    props = make_props(unit="g/h")
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_HIDRO", props)
    mock_coordinator.data = {"MBF_PAR_HIDRO_NOM": 100.0}
    assert ent.native_unit_of_measurement == "%"
    mock_coordinator.data = {"MBF_PAR_HIDRO_NOM": 80.0}
    assert ent.native_unit_of_measurement == "g/h"
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    assert ent.native_unit_of_measurement == "g/h"


def test_native_max_value_dynamic(mock_coordinator):
    props = make_props(max=120.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_HIDRO", props)
    mock_coordinator.data = {"MBF_PAR_HIDRO_NOM": 77.0}
    assert ent.native_max_value == 77.0
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    assert ent.native_max_value == 120.0


def test_icon(mock_coordinator):
    props = make_props(icon="mdi:beaker")
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    assert ent.icon == "mdi:beaker"
    props2 = make_props()
    ent2 = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props2)
    assert ent2.icon is None


@pytest.mark.asyncio
async def test_async_set_native_value_and_debounce(mock_coordinator):
    props = make_props(register=0x0210, scale=2.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    # Patch asyncio.sleep to run immediately
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent.async_set_native_value(6.5)
        await ent._pending_write_task
    # Should have written 13 (6.5*2)
    ent.coordinator.client.async_write_register.assert_awaited_with(
        0x0210, 13, apply=True
    )
    ent.coordinator.async_request_refresh.assert_awaited()


@pytest.mark.asyncio
async def test_debounced_write_no_client(mock_coordinator):
    props = make_props(register=0x0210, scale=2.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    ent.coordinator.client = None
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent._debounced_write()  # Should do nothing, but not crash


@pytest.mark.asyncio
async def test_async_added_to_hass_sets_value(mock_coordinator):
    props = make_props(register=0x0210, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    client = AsyncMock()
    ent.coordinator.client = client
    client.async_read_all = AsyncMock(return_value={"MBF_PAR_PH1": 7.7})
    ent.async_write_ha_state = MagicMock()
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent.async_added_to_hass()
    ent.coordinator.data = {
        "MBF_PAR_PH1": 7.7
    }  # Simulate HA assigning coordinator.data
    assert ent.native_value == 7.7


@pytest.mark.asyncio
async def test_async_added_to_hass_no_client(mock_coordinator):
    props = make_props(register=0x0210, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    ent.coordinator.client = None
    ent.async_write_ha_state = MagicMock()
    # Should log error but not crash
    await ent.async_added_to_hass()
