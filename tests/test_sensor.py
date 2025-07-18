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
from unittest.mock import MagicMock
from custom_components.vistapool.sensor import VistaPoolSensor


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


@pytest.fixture
def sensor_props():
    return {
        "name": "pH Level",
        "unit": "pH",
        "device_class": "ph",
        "state_class": "measurement",
        "icon": "mdi:ph",
    }


def test_sensor_attrs(mock_coordinator, sensor_props):
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_MEASURE_PH", sensor_props
    )
    assert ent._key == "MBF_MEASURE_PH"
    assert ent._attr_device_class == "ph"
    assert ent._attr_state_class == "measurement"
    assert ent.icon == "mdi:ph"


def test_sensor_native_value(mock_coordinator, sensor_props):
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_MEASURE_PH", sensor_props
    )
    mock_coordinator.data["MBF_MEASURE_PH"] = 7.3
    assert ent.native_value == 7.3


def test_sensor_native_value_filtration_off(mock_coordinator, sensor_props):
    ent = VistaPoolSensor(
        mock_coordinator, "test_entry", "MBF_MEASURE_PH", sensor_props
    )
    mock_coordinator.data["Filtration Pump"] = False
    # If "measure_when_filtration_off" is not set, it returns None
    mock_coordinator.config_entry.options = {}
    assert ent.native_value is None
