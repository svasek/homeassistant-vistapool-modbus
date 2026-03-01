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
from custom_components.vistapool.binary_sensor import (
    VistaPoolBinarySensor,
    async_setup_entry,
)


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


@pytest.mark.asyncio
async def test_async_setup_entry_adds_entities(monkeypatch):
    """Test async_setup_entry adds the correct entities."""

    # Prepare a fake coordinator with sample data
    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {
            "MBF_PAR_MODEL": 0x000F,  # All bits set (should allow all modules)
            "MBF_PAR_PH_BASE_RELAY_GPIO": True,
            "MBF_PAR_PH_ACID_RELAY_GPIO": True,
            "Chlorine measurement module detected": True,
            "Redox measurement module detected": True,
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)

    # Entities should be created and passed to async_add_entities
    # The number depends on your BINARY_SENSOR_DEFINITIONS (at least 1 expected)
    assert async_add_entities.call_count == 1
    entities = async_add_entities.call_args[0][0]
    assert isinstance(entities, list)
    # At least one entity, all must be instances of VistaPoolBinarySensor
    from custom_components.vistapool.binary_sensor import VistaPoolBinarySensor

    assert all(isinstance(e, VistaPoolBinarySensor) for e in entities)
    # (Optional) Check that entities have correct keys
    entity_keys = [e._key for e in entities]
    # Should contain at least one expected sensor (by key from BINARY_SENSOR_DEFINITIONS)
    # For example, "pH acid pump active"
    assert any("acid" in k for k in entity_keys)


@pytest.mark.asyncio
async def test_async_setup_entry_no_data(monkeypatch, caplog):
    """Test async_setup_entry returns early if coordinator.data is empty."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    with caplog.at_level("WARNING"):
        await async_setup_entry(hass, entry, async_add_entities)
        # Should log warning
        assert "No data from Modbus" in caplog.text
    # No entities should be added
    async_add_entities.assert_not_called()


@pytest.mark.asyncio
async def test_async_setup_entry_option_disables_sensor(monkeypatch):
    """Test that sensors with options=False are skipped."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {"sensor_option": False}

    class DummyCoordinator:
        data = {"MBF_PAR_MODEL": 0x0001}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    # Patch BINARY_SENSOR_DEFINITIONS for this test
    from custom_components.vistapool import binary_sensor as bs_module

    bs_module.BINARY_SENSOR_DEFINITIONS["Some Option Sensor"] = {
        "option": "sensor_option"
    }

    await async_setup_entry(hass, entry, async_add_entities)
    # Should only add sensors without "option" or with option True
    entities = async_add_entities.call_args[0][0]
    assert not any(e._key == "Some Option Sensor" for e in entities)


@pytest.mark.asyncio
async def test_async_setup_entry_skips_pool_cover_when_not_enabled(monkeypatch):
    """Test that Pool Cover sensor is skipped when cover function is not enabled."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {
            "MBF_PAR_MODEL": 0x0002,  # Hidro module present
            "MBF_PAR_HIDRO_COVER_ENABLE": 0x0000,  # Cover function disabled (bit 0 = 0)
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    # Pool Cover should NOT be in entities
    assert not any(e._key == "Pool Cover" for e in entities)


@pytest.mark.asyncio
async def test_async_setup_entry_includes_pool_cover_when_enabled(monkeypatch):
    """Test that Pool Cover sensor is included when cover function is enabled."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {
            "MBF_PAR_MODEL": 0x0002,  # Hidro module present
            "MBF_PAR_HIDRO_COVER_ENABLE": 0x0001,  # Cover function enabled (bit 0 = 1)
        }
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    # Pool Cover SHOULD be in entities
    assert any(e._key == "Pool Cover" for e in entities)


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


def test_is_on_pool_cover_inverted(mock_coordinator):
    """Test Pool Cover has inverted logic for OPENING device class."""
    props = make_props()
    ent = VistaPoolBinarySensor(mock_coordinator, "test_entry", "Pool Cover", props)
    # Hardware: 1 = cover active (pool covered) -> HA: OFF (closed)
    mock_coordinator.data = {"Pool Cover": True}
    assert ent.is_on is False
    # Hardware: 0 = cover inactive (pool uncovered) -> HA: ON (open)
    mock_coordinator.data = {"Pool Cover": False}
    assert ent.is_on is True


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
