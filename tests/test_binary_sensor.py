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
from custom_components.vistapool.binary_sensor import VistaPoolBinarySensor


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    mock.config_entry.entry_id = "test_entry"
    return mock


def make_props(**kwargs):
    d = {}
    d.update(kwargs)
    return d


def test_is_on_direct_key(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "pH acid pump active", props
    )
    mock_coordinator.data = {"pH acid pump active": True}
    assert ent.is_on is True
    mock_coordinator.data = {"pH acid pump active": False}
    assert ent.is_on is False


def test_is_on_device_time_out_of_sync(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "Device Time Out Of Sync", props
    )
    with patch(
        "custom_components.vistapool.binary_sensor.is_device_time_out_of_sync",
        return_value=True,
    ):
        assert ent.is_on is True
    with patch(
        "custom_components.vistapool.binary_sensor.is_device_time_out_of_sync",
        return_value=False,
    ):
        assert ent.is_on is False


def test_is_on_measurement_module_filtration_pump_off(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "pH measurement active", props
    )
    mock_coordinator.data = {"Filtration Pump": False, "pH measurement active": True}
    # Filtration off disables sensor
    assert ent.is_on is False
    # If pump is on, returns True
    mock_coordinator.data = {"Filtration Pump": True, "pH measurement active": True}
    assert ent.is_on is True


def test_is_on_status_dict(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "MBF_STATUS_pump_on", props
    )
    mock_coordinator.data = {"MBF_STATUS": {"pump_on": True, "other": False}}
    assert ent.is_on is True
    mock_coordinator.data = {"MBF_STATUS": {"pump_on": False}}
    assert ent.is_on is False
    # Status not a dict
    mock_coordinator.data = {"MBF_STATUS": None}
    assert ent.is_on is False


def test_icon_on_off(mock_coordinator):
    props = make_props(icon_on="mdi:pump", icon_off="mdi:pump-off")
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "pH acid pump active", props
    )
    mock_coordinator.data = {"pH acid pump active": True}
    assert ent.icon == "mdi:pump"
    mock_coordinator.data = {"pH acid pump active": False}
    assert ent.icon == "mdi:pump-off"


def test_native_value(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "pH acid pump active", props
    )
    mock_coordinator.data = {"pH acid pump active": True}
    assert ent.native_value is True
    mock_coordinator.data = {}
    assert ent.native_value is None


@pytest.mark.asyncio
async def test_async_added_to_hass_calls_super(mock_coordinator):
    props = make_props()
    ent = VistaPoolBinarySensor(
        mock_coordinator, "test_entry", "pH acid pump active", props
    )
    with patch(
        "custom_components.vistapool.binary_sensor.VistaPoolEntity.async_added_to_hass",
        return_value=None,
    ) as parent:
        await ent.async_added_to_hass()
        parent.assert_called_once()
