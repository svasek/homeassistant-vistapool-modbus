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
from custom_components.vistapool.switch import VistaPoolSwitch


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
def switch_props():
    return {
        "switch_type": "aux",
        "relay_index": 1,
        "icon_on": "mdi:toggle-switch",
        "icon_off": "mdi:toggle-switch-off",
    }


def test_switch_attrs(mock_coordinator, switch_props):
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "AUX1", switch_props)
    assert ent._key == "AUX1"
    assert ent._switch_type == "aux"
    assert ent._relay_index == 1
    assert ent.icon == "mdi:toggle-switch-off"


def test_switch_is_on(mock_coordinator, switch_props):
    ent = VistaPoolSwitch(mock_coordinator, "test_entry", "AUX1", switch_props)
    mock_coordinator.data["AUX1"] = True
    assert ent.is_on is True
    mock_coordinator.data["AUX1"] = False
    assert ent.is_on is False
