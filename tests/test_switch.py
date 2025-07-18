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
from custom_components.vistapool.switch import VistaPoolSwitch


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


@pytest.mark.asyncio
async def test_turn_on_manual_filtration(mock_coordinator):
    props = make_props(switch_type="manual_filtration")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "manual", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_on()
    ent.coordinator.client.async_write_register.assert_awaited_with(0x0413, 1)


@pytest.mark.asyncio
async def test_turn_off_manual_filtration(mock_coordinator):
    props = make_props(switch_type="manual_filtration")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "manual", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_off()
    ent.coordinator.client.async_write_register.assert_awaited_with(0x0413, 0)


@pytest.mark.asyncio
async def test_turn_on_aux(mock_coordinator):
    props = make_props(switch_type="aux", relay_index=2)
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux2", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_on()
    ent.coordinator.client.async_write_aux_relay.assert_awaited_with(2, True)


@pytest.mark.asyncio
async def test_turn_off_aux(mock_coordinator):
    props = make_props(switch_type="aux", relay_index=2)
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux2", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_off()
    ent.coordinator.client.async_write_aux_relay.assert_awaited_with(2, False)


@pytest.mark.asyncio
async def test_turn_on_auto_time_sync(mock_coordinator):
    props = make_props(switch_type="auto_time_sync")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "sync", props)
    ent.coordinator.set_auto_time_sync = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_on()
    ent.coordinator.set_auto_time_sync.assert_awaited_with(True)


@pytest.mark.asyncio
async def test_turn_off_auto_time_sync(mock_coordinator):
    props = make_props(switch_type="auto_time_sync")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "sync", props)
    ent.coordinator.set_auto_time_sync = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_off()
    ent.coordinator.set_auto_time_sync.assert_awaited_with(False)


@pytest.mark.asyncio
async def test_turn_on_relay_timer(mock_coordinator):
    props = make_props(
        switch_type="relay_timer",
        function_addr=0x0100,
        function_code=7,
        timer_block_addr=0x0200,
    )
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_on()
    ent.coordinator.client.async_write_register.assert_any_await(0x0100, 7)
    ent.coordinator.client.async_write_register.assert_any_await(0x0200, 3)
    ent.coordinator.client.async_write_register.assert_any_await(0x02F5, 1)


@pytest.mark.asyncio
async def test_turn_off_relay_timer(mock_coordinator):
    props = make_props(switch_type="relay_timer", timer_block_addr=0x0200)
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_off()
    ent.coordinator.client.async_write_register.assert_any_await(0x0200, 4)
    ent.coordinator.client.async_write_register.assert_any_await(0x02F5, 1)


def test_is_on_manual_filtration_on(mock_coordinator):
    props = make_props(switch_type="manual_filtration")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "manual", props)
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 0, "MBF_PAR_FILT_MANUAL_STATE": 1}
    assert ent.is_on is True


def test_is_on_manual_filtration_off(mock_coordinator):
    props = make_props(switch_type="manual_filtration")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "manual", props)
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 0, "MBF_PAR_FILT_MANUAL_STATE": 0}
    assert ent.is_on is False


def test_is_on_aux(mock_coordinator):
    props = make_props(switch_type="aux")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    mock_coordinator.data = {"aux1": True}
    assert ent.is_on is True


def test_is_on_relay_timer(mock_coordinator):
    props = make_props(switch_type="relay_timer")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    mock_coordinator.data = {"relay_aux1_enable": 3}
    assert ent.is_on is True


def test_available_manual_filtration(mock_coordinator):
    props = make_props(switch_type="manual_filtration")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "manual", props)
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 0}
    assert ent.available is True
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 1}
    assert ent.available is False


def test_available_relay_timer_aux(mock_coordinator):
    props = make_props(switch_type="relay_timer")
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    mock_coordinator.data = {"relay_aux1_enable": 3}
    assert ent.available is True
    mock_coordinator.data = {"relay_aux1_enable": 0}
    assert ent.available is False


def test_icon_on_off(mock_coordinator):
    props = make_props(
        switch_type="aux", icon_on="mdi:lightbulb-on", icon_off="mdi:lightbulb-off"
    )
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "aux1", props)
    mock_coordinator.data = {"aux1": True}
    assert ent.icon == "mdi:lightbulb-on"
    mock_coordinator.data = {"aux1": False}
    assert ent.icon == "mdi:lightbulb-off"
