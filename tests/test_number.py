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
from custom_components.vistapool.number import VistaPoolNumber


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.unique_id = "test_slug"
    mock.config_entry = config_entry
    return mock


@pytest.fixture
def number_props():
    return {
        "register": 0x0100,
        "unit": "°C",
        "min": 10,
        "max": 30,
        "step": 1,
        "icon": "mdi:thermometer",
    }


def test_number_attrs(mock_coordinator, number_props):
    ent = VistaPoolNumber(
        mock_coordinator, "test_entry", "MBF_PAR_HEATING_TEMP", number_props
    )
    assert ent._key == "MBF_PAR_HEATING_TEMP"
    assert ent._register == 0x0100
    assert ent.native_unit_of_measurement == "°C"
    assert ent.icon == "mdi:thermometer"


def test_number_native_value(mock_coordinator, number_props):
    ent = VistaPoolNumber(
        mock_coordinator, "test_entry", "MBF_PAR_HEATING_TEMP", number_props
    )
    mock_coordinator.data["MBF_PAR_HEATING_TEMP"] = 24
    assert ent.native_value == 24
