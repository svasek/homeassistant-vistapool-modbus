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

from custom_components.vistapool.binary_sensor import VistaPoolBinarySensor


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    # Prepare config_entry exactly as required by the entity
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.unique_id = "test_slug"
    mock.config_entry = config_entry
    return mock


@pytest.fixture
def sensor_props():
    return {
        "device_class": "power",
        "entity_category": None,
        "icon_on": "mdi:pump",
        "icon_off": "mdi:pump-off",
        "enabled_default": True,
    }


def test_binary_sensor_state_on_and_icon_on(mock_coordinator, sensor_props):
    ent = VistaPoolBinarySensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        key="is_pump_on",
        props=sensor_props,
    )
    ent._attr_suggested_object_id = "vistapool_pump_on"
    ent.coordinator.data["is_pump_on"] = True
    assert ent.is_on is True
    assert ent.icon == "mdi:pump"


def test_binary_sensor_state_off_and_icon_off(mock_coordinator, sensor_props):
    ent = VistaPoolBinarySensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        key="is_pump_on",
        props=sensor_props,
    )
    ent._attr_suggested_object_id = "vistapool_pump_on"
    ent.coordinator.data["is_pump_on"] = False
    assert ent.is_on is False
    assert ent.icon == "mdi:pump-off"


def test_binary_sensor_missing_key(mock_coordinator, sensor_props):
    ent = VistaPoolBinarySensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        key="is_nonexistent",
        props=sensor_props,
    )
    # If the key is not in the data, it returns False
    assert ent.is_on is False
