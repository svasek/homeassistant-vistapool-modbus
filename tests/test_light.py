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
from custom_components.vistapool.light import VistaPoolLight


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
def light_props():
    return {
        "switch_type": "relay_timer",
        "icon_on": "mdi:lightbulb-on",
        "icon_off": "mdi:lightbulb-off",
    }


def test_light_attrs(mock_coordinator, light_props):
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    assert ent._key == "light"
    assert ent._switch_type == "relay_timer"
    assert ent.icon == "mdi:lightbulb-off"


def test_light_is_on(mock_coordinator, light_props):
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    mock_coordinator.data["relay_light_enable"] = 3
    assert ent.is_on is True
    mock_coordinator.data["relay_light_enable"] = 4
    assert ent.is_on is False
