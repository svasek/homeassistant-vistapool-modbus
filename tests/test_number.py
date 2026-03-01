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
from unittest.mock import MagicMock, AsyncMock, patch, call
from custom_components.vistapool.const import (
    HEATING_SETPOINT_REGISTER,
    INTELLIGENT_SETPOINT_REGISTER,
)
from custom_components.vistapool.number import VistaPoolNumber, async_setup_entry


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

    # Test percent mode with force percentage bit
    mock_coordinator.data = {
        "MBF_PAR_HIDRO_NOM": 100.0,
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x4000,  # Force percentage
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.native_unit_of_measurement == "%"

    # Test g/h mode with force g/h bit
    mock_coordinator.data = {
        "MBF_PAR_HIDRO_NOM": 80.0,
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x2000,  # Force g/h
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.native_unit_of_measurement == "g/h"

    # Test HIDROLIFE machine (should be g/h)
    mock_coordinator.data = {
        "MBF_PAR_HIDRO_NOM": 100.0,
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,
        "MBF_PAR_UICFG_MACHINE": 1,  # HIDROLIFE
    }
    assert ent.native_unit_of_measurement == "g/h"

    # Test default case (should be %)
    mock_coordinator.data = {
        "MBF_PAR_HIDRO_NOM": 100.0,
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,
        "MBF_PAR_UICFG_MACHINE": 2,  # AQUASCENIC
    }
    assert ent.native_unit_of_measurement == "%"

    # Test other number entities return their default unit
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
async def test_debounced_write_mirrors_setpoints_from_heating_register(
    mock_coordinator,
):
    """When editing heating setpoint, both HEATING and INTELLIGENT registers must be written."""
    props = make_props(register=HEATING_SETPOINT_REGISTER, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_HEATING_TEMP", props)
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent.async_set_native_value(28)
        await ent._pending_write_task
    # Expect two ordered writes: first to HEATING, then to INTELLIGENT with apply=True
    ent.coordinator.client.async_write_register.assert_has_awaits(
        [
            call(HEATING_SETPOINT_REGISTER, 28),
            call(INTELLIGENT_SETPOINT_REGISTER, 28, apply=True),
        ]
    )
    ent.coordinator.async_request_refresh.assert_awaited()


@pytest.mark.asyncio
async def test_debounced_write_mirrors_setpoints_from_intelligent_register(
    mock_coordinator,
):
    """When editing intelligent setpoint, both HEATING and INTELLIGENT registers must be written."""
    props = make_props(register=INTELLIGENT_SETPOINT_REGISTER, scale=1.0)
    ent = VistaPoolNumber(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_TEMP", props
    )
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent.async_set_native_value(26)
        await ent._pending_write_task
    ent.coordinator.client.async_write_register.assert_has_awaits(
        [
            call(HEATING_SETPOINT_REGISTER, 26),
            call(INTELLIGENT_SETPOINT_REGISTER, 26, apply=True),
        ]
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


@pytest.mark.asyncio
async def test_async_added_to_hass_sets_value_none(mock_coordinator):
    """Test async_added_to_hass sets native_value to None if key not present."""
    props = make_props(register=0x0210, scale=1.0)
    ent = VistaPoolNumber(mock_coordinator, "test_entry", "MBF_PAR_PH1", props)
    client = AsyncMock()
    ent.coordinator.client = client
    # async_read_all returns a dict, but missing the key
    client.async_read_all = AsyncMock(return_value={"OTHER_KEY": 42.0})
    ent.async_write_ha_state = MagicMock()
    with patch("custom_components.vistapool.number.asyncio.sleep", AsyncMock()):
        await ent.async_added_to_hass()
    # _attr_native_value should be None
    assert ent._attr_native_value is None


@pytest.mark.asyncio
async def test_number_async_setup_entry_adds_entities(monkeypatch):
    """Test async_setup_entry adds number entities for valid data."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        # Simulate all relays assigned
        data = {
            "MBF_PAR_HEATING_GPIO": True,
            "MBF_PAR_PH_ACID_RELAY_GPIO": True,
            "MBF_PAR_PH_BASE_RELAY_GPIO": True,
            "Redox measurement module detected": True,
            "Chlorine measurement module detected": True,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    # Patch NUMBER_DEFINITIONS for this test
    from custom_components.vistapool import number as num_module

    num_module.NUMBER_DEFINITIONS["MBF_PAR_HEATING_TEMP"] = {"register": 0x0201}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_PH1"] = {"register": 0x0202}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_PH2"] = {"register": 0x0203}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_RX1"] = {"register": 0x0204}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_CL1"] = {"register": 0x0205}
    num_module.NUMBER_DEFINITIONS["DUMMY"] = {"register": 0x0206}

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    assert any(isinstance(e, VistaPoolNumber) for e in entities)
    # Should include all keys above
    keys = [e._key for e in entities]
    for k in (
        "MBF_PAR_HEATING_TEMP",
        "MBF_PAR_PH1",
        "MBF_PAR_PH2",
        "MBF_PAR_RX1",
        "MBF_PAR_CL1",
        "DUMMY",
    ):
        assert k in keys


@pytest.mark.asyncio
async def test_number_setup_skips_smart_when_no_temp(monkeypatch):
    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {
            "MBF_PAR_TEMPERATURE_ACTIVE": 0,
            "MBF_PAR_HEATING_GPIO": True,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    from custom_components.vistapool import number as num_module

    num_module.NUMBER_DEFINITIONS["MBF_PAR_SMART_TEMP_HIGH"] = {"register": 0x0418}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_SMART_TEMP_LOW"] = {"register": 0x0419}

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_SMART_TEMP_HIGH" not in keys
    assert "MBF_PAR_SMART_TEMP_LOW" not in keys


@pytest.mark.asyncio
async def test_number_async_setup_entry_skips_unassigned(monkeypatch):
    """Test async_setup_entry skips number entities if required relay is missing."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {
            "MBF_PAR_HEATING_GPIO": False,
            "MBF_PAR_PH_ACID_RELAY_GPIO": False,
            "MBF_PAR_PH_BASE_RELAY_GPIO": False,
            "Redox measurement module detected": False,
            "Chlorine measurement module detected": False,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    from custom_components.vistapool import number as num_module

    num_module.NUMBER_DEFINITIONS["MBF_PAR_HEATING_TEMP"] = {"register": 0x0201}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_PH1"] = {"register": 0x0202}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_PH2"] = {"register": 0x0203}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_RX1"] = {"register": 0x0204}
    num_module.NUMBER_DEFINITIONS["MBF_PAR_CL1"] = {"register": 0x0205}

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    # Should not include any filtered-out keys
    assert "MBF_PAR_HEATING_TEMP" not in keys
    assert "MBF_PAR_PH1" not in keys
    assert "MBF_PAR_PH2" not in keys
    assert "MBF_PAR_RX1" not in keys
    assert "MBF_PAR_CL1" not in keys
