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
from custom_components.vistapool.select import (
    VistaPoolSelect,
    PERIOD_MAP,
    PERIOD_SECONDS_TO_KEY,
)


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.unique_id = "test_slug"
    config_entry.options = {}
    mock.config_entry = config_entry
    return mock


def make_props(**kwargs):
    d = {}
    d.update(kwargs)
    return d


def test_options_basic_options_map(mock_coordinator):
    props = make_props(options_map={0: "auto", 1: "manual", 2: "off"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {}
    opts = ent.options
    assert set(opts) <= {"auto", "manual", "off"}


def test_options_hide_heating_intelligent(mock_coordinator):
    props = make_props(
        options_map={0: "auto", 2: "heating", 3: "intelligent", 4: "off"}
    )
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {"MBF_PAR_HEATING_MODE": 0, "MBF_PAR_TEMPERATURE_ACTIVE": 0}
    opts = ent.options
    assert "heating" not in opts and "intelligent" not in opts


def test_options_hide_smart_temp_sensor(mock_coordinator):
    props = make_props(options_map={0: "auto", 3: "smart", 4: "off"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {"MBF_PAR_HEATING_MODE": 0, "MBF_PAR_TEMPERATURE_ACTIVE": 0}
    opts = ent.options
    assert "smart" not in opts


def test_options_add_backwash(mock_coordinator):
    props = make_props(options_map={0: "auto", 1: "manual", 2: "off", 13: "backwash"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {}
    mock_coordinator.config_entry.options = {"enable_backwash_option": True}
    opts = ent.options
    assert "backwash" in opts


def test_options_timer_time(mock_coordinator):
    from custom_components.vistapool.helpers import (
        hhmm_to_seconds,
        generate_time_options,
    )

    props = make_props(select_type="timer_time")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_start", props)
    mock_coordinator.data = {"relay_aux1_start": 0}
    mock_coordinator.config_entry.options = {"timer_resolution": 5}
    opts = ent.options
    assert all(isinstance(x, str) for x in opts)


def test_options_timer_period(mock_coordinator):
    props = make_props(select_type="timer_period")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_period", props)
    mock_coordinator.data = {"relay_aux1_period": 600}
    opts = ent.options
    assert any(isinstance(x, str) for x in opts)


def test_options_relay_mode_disabled(mock_coordinator):
    props = make_props(select_type="relay_mode", options_map={1: "auto"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_enable", props)
    mock_coordinator.data = {"relay_aux1_enable": 0}
    opts = ent.options
    assert "disabled" in opts


def test_options_boost_hide_redox(mock_coordinator):
    props = make_props(
        options_map={
            0: "inactive",
            1: "active (redox disabled)",
            2: "active (redox enabled)",
        }
    )
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_CELL_BOOST", props)
    mock_coordinator.data = {"Redox measurement module detected": False}
    opts = ent.options
    assert "active (redox enabled)" not in opts


def test_current_option_cell_boost(mock_coordinator):
    props = make_props(
        options_map={
            0: "inactive",
            1: "active (redox disabled)",
            2: "active (redox enabled)",
        }
    )
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_CELL_BOOST", props)
    mock_coordinator.data = {"MBF_CELL_BOOST": 0x8000}
    assert ent.current_option == "active (redox disabled)"
    mock_coordinator.data["MBF_CELL_BOOST"] = 0x05A0
    assert ent.current_option == "active (redox enabled)"


def test_current_option_filtration_speed(mock_coordinator):
    props = {
        "options_map": {0: "low", 1: "mid", 2: "high"},
        "mask": 0x70,
        "shift": 4,
    }
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_FILTRATION_SPEED", props
    )
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 32}
    assert ent.current_option == "high"
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 16}
    assert ent.current_option == "mid"
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 0}
    assert ent.current_option == "low"


def test_current_option_timer_period(mock_coordinator):
    props = make_props(select_type="timer_period")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_period", props)
    value = list(PERIOD_MAP.values())[0]
    mock_coordinator.data = {"relay_aux1_period": value}
    assert ent.current_option == PERIOD_SECONDS_TO_KEY[value]


def test_current_option_relay_mode(mock_coordinator):
    props = make_props(select_type="relay_mode", options_map={1: "auto", 2: "manual"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_enable", props)
    mock_coordinator.data = {"relay_aux1_enable": 0}
    assert ent.current_option == "disabled"
    mock_coordinator.data["relay_aux1_enable"] = 2
    assert ent.current_option == "auto_linked"


def test_current_option_default(mock_coordinator):
    props = make_props(options_map={0: "auto", 1: "manual", 2: "off"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 1}
    assert ent.current_option == "manual"


@pytest.mark.asyncio
async def test_async_select_option_timer_time(mock_coordinator):
    props = make_props(select_type="timer_time")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_start", props)
    ent.hass = MagicMock()
    ent.hass.services.async_call = AsyncMock()
    mock_coordinator.data = {"relay_aux1_stop": 0}
    await ent.async_select_option("06:00")
    ent.hass.services.async_call.assert_awaited()


@pytest.mark.asyncio
async def test_async_select_option_timer_period(mock_coordinator):
    props = make_props(select_type="timer_period")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_period", props)
    ent.hass = MagicMock()
    ent.hass.services.async_call = AsyncMock()
    await ent.async_select_option("10")
    ent.hass.services.async_call.assert_awaited()


@pytest.mark.asyncio
async def test_async_select_option_relay_mode(mock_coordinator):
    props = make_props(select_type="relay_mode", options_map={0: "auto", 1: "manual"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_enable", props)
    ent.hass = MagicMock()
    ent.hass.services.async_call = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_select_option("manual")
    ent.hass.services.async_call.assert_awaited()
    ent.coordinator.async_request_refresh.assert_awaited()
    ent.async_write_ha_state.assert_called()


@pytest.mark.asyncio
async def test_async_select_option_backwash(mock_coordinator):
    props = make_props(options_map={0: "auto", 1: "manual", 13: "backwash"})
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    ent.hass = MagicMock()
    ent.hass.services.async_call = AsyncMock()
    ent.coordinator.data = {}
    ent.coordinator.device_name = "vistapool"
    # Should log info, but not call anything else
    await ent.async_select_option("backwash")


@pytest.mark.asyncio
async def test_async_select_option_cell_boost(mock_coordinator):
    props = make_props(
        options_map={
            0: "inactive",
            1: "active (redox disabled)",
            2: "active (redox enabled)",
        }
    )
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_CELL_BOOST", props)
    ent.hass = MagicMock()
    ent.coordinator.client = AsyncMock()
    await ent.async_select_option("active (redox enabled)")
    ent.coordinator.client.async_write_register.assert_awaited()


@pytest.mark.asyncio
async def test_async_select_option_filtration_speed(mock_coordinator):
    props = {
        "options_map": {0: "low", 1: "mid", 2: "high"},
        "mask": 0x70,
        "shift": 4,
        "register": 0x050F,
    }
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_FILTRATION_SPEED", props
    )
    ent.hass = MagicMock()
    ent.coordinator.client = AsyncMock()
    ent.coordinator.device_name = "vistapool"
    # Start with current=0 (should be "low"). Set to "mid" (1).
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 0}
    await ent.async_select_option("mid")
    ent.coordinator.client.async_write_register.assert_awaited_with(
        0x050F, 16, apply=True
    )
    # Now try "high"
    ent.coordinator.client.reset_mock()
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 0}
    await ent.async_select_option("high")
    ent.coordinator.client.async_write_register.assert_awaited_with(
        0x050F, 32, apply=True
    )


@pytest.mark.asyncio
async def test_async_select_option_default(mock_coordinator):
    props = make_props(options_map={0: "auto", 1: "manual", 2: "off"}, register=0x0200)
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    ent.hass = MagicMock()
    ent.coordinator.client = AsyncMock()
    ent.coordinator.data = {"MBF_PAR_FILT_MODE": 1}
    ent.coordinator.async_request_refresh = AsyncMock()  # Přidat!
    ent.async_write_ha_state = MagicMock()  # Pokud je v metodě
    await ent.async_select_option("manual")
    ent.coordinator.client.async_write_register.assert_awaited()
