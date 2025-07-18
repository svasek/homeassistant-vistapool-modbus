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
    mock.config_entry = config_entry
    return mock


@pytest.fixture
def select_props():
    return {
        "options_map": {0: "auto", 1: "manual", 2: "off"},
        "icon": "mdi:select",
        "select_type": None,
    }


def test_select_attrs(mock_coordinator, select_props):
    # explicitly set the backwash option to True or False depending on what we want to test
    mock_coordinator.config_entry.options = {"enable_backwash_option": True}
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", select_props
    )
    assert ent._key == "MBF_PAR_FILT_MODE"
    assert ent.options == ["auto", "manual", "off", "backwash"]


def test_select_current_option(mock_coordinator, select_props):
    ent = VistaPoolSelect(
        mock_coordinator, "test_entry", "MBF_PAR_FILT_MODE", select_props
    )
    mock_coordinator.data["MBF_PAR_FILT_MODE"] = 1
    # 1 -> "manual"
    assert ent.current_option == "manual"
    mock_coordinator.data["MBF_PAR_FILT_MODE"] = 2
    assert ent.current_option == "off"
