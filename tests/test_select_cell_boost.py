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
from custom_components.vistapool.select import VistaPoolSelect


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
def boost_props():
    return {
        "options_map": {
            0: "inactive",
            1: "active (redox disabled)",
            2: "active (redox enabled)",
        },
        "icon": "mdi:lightning-bolt",
    }


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
