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

import pytest, asyncio
from unittest.mock import MagicMock, AsyncMock, Mock, patch
from custom_components.vistapool.select import (
    VistaPoolSelect,
    VistaPoolEntity,
    PERIOD_MAP,
    PERIOD_SECONDS_TO_KEY,
    async_setup_entry,
)


@pytest.fixture(autouse=True)
def _fast_sleep(monkeypatch):
    """Patch asyncio.sleep to a no-op for all tests in this module to speed them up."""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())


@pytest.fixture
def mock_coordinator():
    mock = AsyncMock()
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


@pytest.fixture
def boost_props():
    return {
        "options_map": {
            0: "inactive",
            1: "active (redox disabled)",
            2: "active (redox enabled)",
        },
        "icon": "mdi:lightning-bolt",
    }


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


def _intelligent_min_time_props():
    return {
        "options_map": {
            120: "2h",
            180: "3h",
            240: "4h",
            300: "5h",
            360: "6h",
            420: "7h",
            480: "8h",
            540: "9h",
            600: "10h",
            660: "11h",
            720: "12h",
        },
        "register": 0x041D,
    }


def test_options_intelligent_min_time_unknown_value(mock_coordinator):
    props = _intelligent_min_time_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_FILT_MIN_TIME", props
    )
    # Known value → just labels, no numeric prefix
    mock_coordinator.data = {"MBF_PAR_INTELLIGENT_FILT_MIN_TIME": 360}
    opts = ent.options
    assert opts[0] == "2h" and "6h" in opts
    # Unknown value → prepend numeric string with 'm'
    mock_coordinator.data = {"MBF_PAR_INTELLIGENT_FILT_MIN_TIME": 365}
    opts = ent.options
    assert opts[0] == "365m"


def test_current_option_intelligent_min_time(mock_coordinator):
    props = _intelligent_min_time_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_FILT_MIN_TIME", props
    )
    mock_coordinator.data = {"MBF_PAR_INTELLIGENT_FILT_MIN_TIME": 360}
    assert ent.current_option == "6h"
    mock_coordinator.data = {"MBF_PAR_INTELLIGENT_FILT_MIN_TIME": 365}
    assert ent.current_option == "365m"


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
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = Mock()
    await ent.async_select_option("manual")
    ent.coordinator.client.async_write_register.assert_awaited()


@pytest.mark.asyncio
async def test_async_select_option_intelligent_min_time_label(mock_coordinator):
    props = _intelligent_min_time_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_FILT_MIN_TIME", props
    )
    ent.hass = MagicMock()
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = Mock()
    await ent.async_select_option("6h")
    ent.coordinator.client.async_write_register.assert_awaited_with(0x041D, 360)


@pytest.mark.asyncio
async def test_async_select_option_intelligent_min_time_numeric(mock_coordinator):
    props = _intelligent_min_time_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_FILT_MIN_TIME", props
    )
    ent.hass = MagicMock()
    ent.coordinator.client = AsyncMock()
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = Mock()
    await ent.async_select_option("365m")
    ent.coordinator.client.async_write_register.assert_awaited_with(0x041D, 365)


def test_select_cell_boost_current_option(mock_coordinator, boost_props):
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_CELL_BOOST", boost_props)

    # case: Inactive
    mock_coordinator.data["MBF_CELL_BOOST"] = 0
    assert ent.current_option == "inactive"

    # case: Active (redox disabled)
    mock_coordinator.data["MBF_CELL_BOOST"] = 0x8000  # bit 0x8000 set
    assert ent.current_option == "active (redox disabled)"

    # case: Active (redox enabled)
    mock_coordinator.data["MBF_CELL_BOOST"] = 0x05A0  # 0x0500 | 0x00A0
    assert ent.current_option == "active (redox enabled)"

    # fallback
    mock_coordinator.data["MBF_CELL_BOOST"] = 12345  # invalid value
    assert ent.current_option == "inactive"


def test_select_filtration_speed_current_option(mock_coordinator):
    props = make_props(
        options_map={0: "low", 1: "mid", 2: "high"}, mask=0x0070, shift=4
    )
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_FILTRATION_SPEED", props
    )
    # mask=0x0070, shift=4; tedy 16 => 1 (mid)
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 16}
    assert ent.current_option == "mid"
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 0}
    assert ent.current_option == "low"
    mock_coordinator.data = {"MBF_PAR_FILTRATION_CONF": 32}
    assert ent.current_option == "high"


@pytest.mark.asyncio
async def test_select_async_setup_entry_adds_entities(monkeypatch):
    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        # FILTRATION_CONF: 1 → get_filtration_pump_type=True, MBF_CELL_BOOST: model OK
        data = {
            "MBF_PAR_FILTRATION_CONF": 1,
            "MBF_PAR_MODEL": 0x0002,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    # Patch SELECT_DEFINITIONS to make the test predictable
    from custom_components.vistapool import select as select_module

    select_module.SELECT_DEFINITIONS["MBF_PAR_FILTRATION_SPEED"] = {"option": None}
    select_module.SELECT_DEFINITIONS["MBF_CELL_BOOST"] = {"option": None}

    # Patch get_filtration_pump_type to always return True
    monkeypatch.setattr(
        "custom_components.vistapool.select.get_filtration_pump_type", lambda x: True
    )

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_FILTRATION_SPEED" in keys
    assert "MBF_CELL_BOOST" in keys


@pytest.mark.asyncio
async def test_select_async_setup_entry_option_disabled(monkeypatch):
    class DummyEntry:
        entry_id = "test_entry"
        options = {"test_option": False}

    class DummyCoordinator:
        data = {"MBF_PAR_FILTRATION_CONF": 1, "MBF_PAR_MODEL": 0x0002}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()
    from custom_components.vistapool import select as select_module

    select_module.SELECT_DEFINITIONS["TEST_SELECT"] = {"option": "test_option"}
    monkeypatch.setattr(
        "custom_components.vistapool.select.get_filtration_pump_type", lambda x: True
    )

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    # Should not include TEST_SELECT, as option is False
    assert "TEST_SELECT" not in keys


@pytest.mark.asyncio
async def test_select_async_setup_entry_no_data(caplog):
    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)
    async_add_entities.assert_not_called()
    assert "No data from Modbus" in caplog.text


@pytest.mark.asyncio
async def test_async_added_to_hass_calls_super(mock_coordinator):
    props = make_props()
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    with patch.object(VistaPoolEntity, "async_added_to_hass", AsyncMock()) as sup:
        await ent.async_added_to_hass()
        sup.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_select_option_stop_field(mock_coordinator):
    props = make_props(select_type="timer_time")
    ent = VistaPoolSelect(mock_coordinator, "test_entry", "relay_aux1_stop", props)
    mock_coordinator.data = {
        "relay_aux1_start": 3600,
        "relay_aux1_stop": 7200,
    }
    mock_coordinator.client = AsyncMock()
    mock_coordinator.client.async_write_register = AsyncMock(return_value=True)
    ent.hass = MagicMock()
    ent.hass.services = AsyncMock()
    ent.hass.services.async_call = AsyncMock(return_value=None)

    option = "03:00"
    with patch.object(ent, "async_write_ha_state", AsyncMock()):
        await ent.async_select_option(option)

    ent.hass.services.async_call.assert_any_call(
        "vistapool",
        "set_timer",
        {
            "entry_id": "test_entry",
            "timer": "relay_aux1",
            "start": "01:00",
            "stop": "03:00",
        },
    )


def test_options_ph_pump_delay(mock_coordinator):
    """Test that the pH pump delay select returns the expected fixed options."""
    props = make_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_RELAY_ACTIVATION_DELAY", props
    )
    mock_coordinator.data = {"MBF_PAR_RELAY_ACTIVATION_DELAY": 20}
    opts = ent.options
    assert "10" in opts and "300" in opts
    # current value should be present even if not in the fixed list
    mock_coordinator.data["MBF_PAR_RELAY_ACTIVATION_DELAY"] = 25
    opts = ent.options
    assert "25" in opts


def test_current_option_ph_pump_delay(mock_coordinator):
    """Test that current_option returns the delay in seconds as string."""
    props = make_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_RELAY_ACTIVATION_DELAY", props
    )
    mock_coordinator.data = {"MBF_PAR_RELAY_ACTIVATION_DELAY": 120}
    assert ent.current_option == "120"
    mock_coordinator.data["MBF_PAR_RELAY_ACTIVATION_DELAY"] = None
    assert ent.current_option is None


@pytest.mark.asyncio
async def test_async_select_option_ph_pump_delay(mock_coordinator):
    """Test that selecting a delay writes (value - 10) to register 0x0433."""
    props = make_props()
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_RELAY_ACTIVATION_DELAY", props
    )
    mock_coordinator.client = AsyncMock()
    ent.coordinator.client = mock_coordinator.client
    ent.coordinator.async_request_refresh = AsyncMock()
    ent.async_write_ha_state = Mock()

    # Select 180s -> should write 170 (device internally adds 10s)
    await ent.async_select_option("180")
    ent.coordinator.client.async_write_register.assert_awaited_with(0x0433, 170)
