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
from custom_components.vistapool.sensor import (
    VistaPoolSensor,
    FILTRATION_MODE_MAP,
    PH_STATUS_ALARM_MAP,
    FILTRATION_SPEED_MAP,
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
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_HIDRO_CURRENT", {})
    assert ent.suggested_display_precision == 0
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_MEASURE_CONDUCTIVITY", {}
    )
    assert ent.suggested_display_precision == 0
    ent = VistaPoolSensor(mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", {})
    assert ent.suggested_display_precision is None


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
