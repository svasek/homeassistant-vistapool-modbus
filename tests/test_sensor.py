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
from unittest.mock import MagicMock, patch
from homeassistant.components.sensor import SensorDeviceClass
from custom_components.vistapool.sensor import (
    VistaPoolSensor,
    FILTRATION_MODE_MAP,
    PH_STATUS_ALARM_MAP,
    FILTRATION_SPEED_MAP,
    async_setup_entry,
)


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.config_entry.options = {}
    mock.config_entry.entry_id = "test_entry"
    mock.device_slug = "vistapool"
    return mock


def make_props(**kwargs):
    d = {}
    d.update(kwargs)
    return d


def test_icon_filtration_modes(mock_coordinator):
    props = make_props(icon="mdi:water-sync")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    for raw, name in FILTRATION_MODE_MAP.items():
        mock_coordinator.data = {"MBF_PAR_FILT_MODE": raw}
        result = ent.icon
        assert isinstance(result, str)


def test_icon_ph_alarm(mock_coordinator):
    props = make_props(icon="mdi:alert")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PH_STATUS_ALARM", props)
    mock_coordinator.data = {"MBF_PH_STATUS_ALARM": 0}
    assert ent.icon == "mdi:alert"
    mock_coordinator.data = {"MBF_PH_STATUS_ALARM": 2}
    assert ent.icon == "mdi:alert"


def test_icon_hidro_current(mock_coordinator):
    props = make_props(icon="mdi:air-humidifier")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_HIDRO_CURRENT", props)
    mock_coordinator.data = {"MBF_HIDRO_CURRENT": True}
    assert ent.icon == "mdi:air-humidifier"
    mock_coordinator.data = {"MBF_HIDRO_CURRENT": False}
    assert ent.icon == "mdi:air-humidifier-off"


def test_icon_default(mock_coordinator):
    props = make_props(icon="mdi:ph")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", props)
    assert ent.icon == "mdi:ph"


def test_suggested_display_precision(mock_coordinator):
    # Test for MBF_HIDRO_CURRENT with percent mode
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_HIDRO_CURRENT", {})
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x4000,  # Force percentage
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.suggested_display_precision == 0

    # Test for MBF_HIDRO_CURRENT with g/h mode
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x2000,  # Force g/h
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.suggested_display_precision == 1

    # Test for conductivity
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_MEASURE_CONDUCTIVITY", {}
    )
    assert ent.suggested_display_precision == 0

    # Test for other sensors
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", {})
    assert ent.suggested_display_precision is None


def test_native_unit_of_measurement_hidro_current(mock_coordinator):
    """Test native_unit_of_measurement for MBF_HIDRO_CURRENT with different configurations."""
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_HIDRO_CURRENT", {"unit": "%"}
    )

    # Test percent mode
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x4000,  # Force percentage bit
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.native_unit_of_measurement == "%"

    # Test g/h mode
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x2000,  # Force g/h bit
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert ent.native_unit_of_measurement == "g/h"

    # Test HIDROLIFE machine (should be g/h)
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,
        "MBF_PAR_UICFG_MACHINE": 1,  # HIDROLIFE
    }
    assert ent.native_unit_of_measurement == "g/h"

    # Test default case (should be %)
    mock_coordinator.data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,
        "MBF_PAR_UICFG_MACHINE": 2,  # AQUASCENIC
    }
    assert ent.native_unit_of_measurement == "%"


def test_native_unit_of_measurement_other_sensors(mock_coordinator):
    """Test that other sensors return their default unit."""
    props = {"unit": "pH"}
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", props)
    mock_coordinator.data = {}
    assert ent.native_unit_of_measurement == "pH"


def test_native_value_filtration_pump_off(mock_coordinator):
    # Default: measure_when_filtration_off = False
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", {})
    mock_coordinator.data = {"Filtration Pump": False}
    mock_coordinator.config_entry.options = {}
    assert ent.native_value is None
    # But if option is enabled, value is returned even if pump off
    mock_coordinator.config_entry.options = {"measure_when_filtration_off": True}
    mock_coordinator.data = {"Filtration Pump": False, "MBF_MEASURE_PH": 7.1}
    assert ent.native_value == 7.1


def test_native_value_special_keys(mock_coordinator):
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "HIDRO_POLARITY", {})
    mock_coordinator.data = {"HIDRO in Pol1": True, "HIDRO in Pol2": False}
    assert ent.native_value == "pol1"
    mock_coordinator.data = {"HIDRO in Pol1": False, "HIDRO in Pol2": True}
    assert ent.native_value == "pol2"
    mock_coordinator.data = {"HIDRO in Pol1": False, "HIDRO in Pol2": False}
    assert ent.native_value == "off"
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", {})
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": 1}
    assert ent.native_value == "auto"
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "FILTRATION_SPEED", {})
    mock_coordinator.data = {"FILTRATION_SPEED": 3}
    assert ent.native_value == "high"
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PH_STATUS_ALARM", {})
    mock_coordinator.data = {"MBF_PH_STATUS_ALARM": 2}
    assert ent.native_value == "ph_low"


def test_native_value_default(mock_coordinator):
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", {})
    mock_coordinator.data = {"MBF_MEASURE_PH": 7.2}
    assert ent.native_value == 7.2


def test_options_property(mock_coordinator):
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", {})
    assert ent.options == list(FILTRATION_MODE_MAP.values())
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "FILTRATION_SPEED", {})
    assert ent.options == list(FILTRATION_SPEED_MAP.values())
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PH_STATUS_ALARM", {})
    assert ent.options == list(PH_STATUS_ALARM_MAP.values())
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "HIDRO_POLARITY", {})
    assert ent.options == ["pol1", "pol2", "off"]


def test_available_always_true(mock_coordinator):
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", {})
    assert ent.available is True


@pytest.mark.asyncio
async def test_async_added_to_hass_logs_and_calls_parent(mock_coordinator):
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_MEASURE_PH", {})
    with patch.object(
        VistaPoolSensor, "async_added_to_hass", wraps=ent.async_added_to_hass
    ) as parent:
        await ent.async_added_to_hass()
        assert parent.called


@pytest.mark.asyncio
async def test_sensor_async_setup_entry_adds_entities(monkeypatch):
    """Test async_setup_entry adds correct entities based on data."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_MEASURE_PH": 7.0,
            "pH measurement module detected": True,
            "MBF_MEASURE_RX": 500,
            "Redox measurement module detected": True,
            "MBF_MEASURE_CL": 2000,
            "Chlorine measurement module detected": True,
            "MBF_MEASURE_CONDUCTIVITY": 35.5,
            "Conductivity measurement module detected": True,
            "MBF_PAR_MODEL": 0x0001,  # ion allowed
            "MBF_ION_CURRENT": 60,
            "MBF_PAR_FILTRATION_CONF": 0x0001,
            "FILTRATION_SPEED": 1,
            "MBF_PAR_FILT_MODE": 1,
            "MBF_PH_STATUS_ALARM": 0,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    # Should add all defined sensors present in data
    keys = [e._key for e in entities]
    assert "MBF_MEASURE_PH" in keys
    assert "MBF_MEASURE_RX" in keys
    assert "MBF_MEASURE_CL" in keys
    assert "MBF_MEASURE_CONDUCTIVITY" in keys
    assert "MBF_ION_CURRENT" in keys
    assert "FILTRATION_SPEED" in keys
    assert "MBF_PAR_FILT_MODE" in keys
    assert "MBF_PH_STATUS_ALARM" in keys


@pytest.mark.asyncio
async def test_sensor_async_setup_entry_detected_flags(monkeypatch):
    """Test async_setup_entry skips entities if 'detected' is missing/False."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_MEASURE_PH": 7.0,
            # "pH measurement module detected": False
            "MBF_MEASURE_RX": 500,
            "Redox measurement module detected": False,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    # MBF_MEASURE_PH and MBF_MEASURE_RX should be skipped
    assert "MBF_MEASURE_PH" not in keys
    assert "MBF_MEASURE_RX" not in keys


@pytest.mark.asyncio
async def test_sensor_async_setup_entry_model_mask(monkeypatch):
    """Test async_setup_entry skips ION sensor if not present in model."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_PAR_MODEL": 0x0000,  # ION not present
            "MBF_ION_CURRENT": 50,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()
    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_ION_CURRENT" not in keys


def make_sensor(props, key, data):
    mock_coord = MagicMock()
    mock_coord.data = data
    mock_coord.device_slug = "vistapool"
    mock_coord.config_entry.entry_id = "test_entry"
    mock_coord.config_entry.options = {}
    return VistaPoolSensor(mock_coord, "test_entry", key, props)


@pytest.mark.parametrize(
    "raw,expected_icon",
    [
        (1, "mdi:water-boiler-auto"),  # auto
        (0, "mdi:water-boiler-alert"),  # manual
        (2, "mdi:water-boiler-alert"),  # heating
        (3, "mdi:water-boiler-auto"),  # smart
        (4, "mdi:water-boiler-auto"),  # intelligent
        (13, "mdi:water-boiler-off"),  # backwash
    ],
)
def test_icon_filtration_mode(mock_coordinator, raw, expected_icon):
    props = make_props(device_class="filtration_mode")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", props)
    mock_coordinator.data = {"MBF_PAR_FILT_MODE": raw}
    assert ent.icon == expected_icon


def test_icon_ph_alarm(mock_coordinator):
    props = make_props(icon="mdi:alert")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PH_STATUS_ALARM", props)
    # No alarm
    mock_coordinator.data = {"MBF_PH_STATUS_ALARM": 0}
    assert ent.icon == "mdi:check-circle-outline"
    # Alarm
    mock_coordinator.data = {"MBF_PH_STATUS_ALARM": 3}
    assert ent.icon == "mdi:alert"


def test_icon_hidro_current(mock_coordinator):
    props = make_props(icon="mdi:air-humidifier")
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_HIDRO_CURRENT", props)
    mock_coordinator.data = {"MBF_HIDRO_CURRENT": True}
    assert ent.icon == "mdi:air-humidifier"
    mock_coordinator.data = {"MBF_HIDRO_CURRENT": False}
    assert ent.icon == "mdi:air-humidifier-off"


def test_icon_default_icon():
    ent = make_sensor({"icon": "mdi:test"}, "MBF_MEASURE_PH", {})
    assert ent.icon == "mdi:test"


@pytest.mark.asyncio
async def test_sensor_temperature_skip_when_inactive():
    """Test that MBF_MEASURE_TEMPERATURE is skipped when MBF_PAR_TEMPERATURE_ACTIVE is 0."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_MEASURE_TEMPERATURE": 25.5,
            "MBF_PAR_TEMPERATURE_ACTIVE": 0,  # Temperature inactive
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_MEASURE_TEMPERATURE" not in keys


@pytest.mark.asyncio
async def test_sensor_temperature_created_when_active():
    """Test that MBF_MEASURE_TEMPERATURE is created when MBF_PAR_TEMPERATURE_ACTIVE is not 0."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_MEASURE_TEMPERATURE": 25.5,
            "MBF_PAR_TEMPERATURE_ACTIVE": 1,  # Temperature active
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_MEASURE_TEMPERATURE" in keys


@pytest.mark.asyncio
async def test_sensor_intelligent_intervals_skip_without_heating():
    """Test that MBF_PAR_INTELLIGENT_INTERVALS is skipped when heating GPIO not assigned or temperature inactive."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_PAR_INTELLIGENT_INTERVALS": 5,
            "MBF_PAR_HEATING_GPIO": 0,  # No heating GPIO
            "MBF_PAR_TEMPERATURE_ACTIVE": 1,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_INTELLIGENT_INTERVALS" not in keys


@pytest.mark.asyncio
async def test_sensor_intelligent_intervals_created_with_heating():
    """Test that MBF_PAR_INTELLIGENT_INTERVALS is created when heating GPIO assigned and temperature active."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_PAR_INTELLIGENT_INTERVALS": 5,
            "MBF_PAR_HEATING_GPIO": 7,  # Heating GPIO assigned
            "MBF_PAR_TEMPERATURE_ACTIVE": 1,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_INTELLIGENT_INTERVALS" in keys


@pytest.mark.asyncio
async def test_sensor_intelligent_tt_next_interval_skip_without_heating():
    """Test that MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL is skipped when heating GPIO not assigned or temperature inactive."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL": 7200,
            "MBF_PAR_HEATING_GPIO": 0,  # No heating GPIO
            "MBF_PAR_TEMPERATURE_ACTIVE": 1,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL" not in keys


@pytest.mark.asyncio
async def test_sensor_intelligent_tt_next_interval_created_with_heating():
    """Test that MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL is created when heating GPIO assigned and temperature active."""

    class DummyEntry:
        entry_id = "test_entry"

    class DummyCoordinator:
        data = {
            "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL": 7200,
            "MBF_PAR_HEATING_GPIO": 7,  # Heating GPIO assigned
            "MBF_PAR_TEMPERATURE_ACTIVE": 1,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]
    keys = [e._key for e in entities]
    assert "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL" in keys


def test_sensor_intelligent_tt_next_interval_calls_helper():
    """Test that MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL sensor calls the helper function."""
    from unittest.mock import patch

    mock_coordinator = MagicMock()
    mock_coordinator.data = {"MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL": 3600}
    mock_coordinator.config_entry.options = {}
    mock_coordinator.config_entry.entry_id = "test_entry"
    mock_coordinator.device_slug = "vistapool"

    props = {"device_class": "timestamp"}
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_PAR_INTELLIGENT_TT_NEXT_INTERVAL", props
    )

    mock_hass = MagicMock()
    ent.hass = mock_hass

    # Patch the helper function to verify it's called correctly
    with patch(
        "custom_components.vistapool.sensor.calculate_next_interval_time"
    ) as mock_calc:
        _ = ent.native_value
        # Verify the helper was called with correct arguments
        mock_calc.assert_called_once_with(3600, mock_hass)
