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

import pytest, asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from custom_components.vistapool.light import VistaPoolLight, async_setup_entry


@pytest.fixture(autouse=True)
def _fast_sleep(monkeypatch):
    """Patch asyncio.sleep to a no-op for all tests in this module to speed them up."""
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())


@pytest.fixture
def mock_coordinator():
    mock = MagicMock()
    mock.data = {}
    mock.device_slug = "vistapool"
    mock.client = AsyncMock()
    mock.async_request_refresh = AsyncMock()
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


@pytest.mark.asyncio
async def test_light_async_turn_on(mock_coordinator, light_props):
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    ent.function_addr = 0x0100
    ent.timer_block_addr = 0x0200
    ent.hass = MagicMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_on()
    assert mock_coordinator.client.async_write_register.called


@pytest.mark.asyncio
async def test_light_async_turn_off(mock_coordinator, light_props):
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    ent.function_addr = 0x0100
    ent.timer_block_addr = 0x0200
    ent.hass = MagicMock()
    ent.async_write_ha_state = MagicMock()
    await ent.async_turn_off()
    assert mock_coordinator.client.async_write_register.called


def test_light_icon_on_off(mock_coordinator):
    props = {"switch_type": "relay_timer", "icon_on": "mdi:on", "icon_off": "mdi:off"}
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", props)
    mock_coordinator.data["relay_light_enable"] = 3  # is_on True
    assert ent.icon == "mdi:on"
    mock_coordinator.data["relay_light_enable"] = 4  # is_on False
    assert ent.icon == "mdi:off"


def test_light_icon_attr_only(mock_coordinator):
    props = {"switch_type": "relay_timer", "icon": "mdi:custom"}
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", props)
    # No _icon_on/_icon_off, fallback to _attr_icon
    assert ent.icon == "mdi:custom"


def test_light_icon_none(mock_coordinator):
    props = {"switch_type": "relay_timer"}
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", props)
    # No icons at all
    assert ent.icon is None


def test_light_available_relay_timer(mock_coordinator, light_props):
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    # Should be available for 0, 3, 4
    for val in (0, 3, 4):
        mock_coordinator.data["relay_light_enable"] = val
        assert ent.available is True
    # Should be unavailable for other values
    mock_coordinator.data["relay_light_enable"] = 2
    assert ent.available is False


def test_light_available_other_type(mock_coordinator):
    props = {"switch_type": "other_type"}
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", props)
    # For non-relay_timer always available
    assert ent.available is True


@pytest.mark.asyncio
async def test_light_async_setup_entry_adds_entities(monkeypatch):
    """Test async_setup_entry adds light entities for enabled lights."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {}

    class DummyCoordinator:
        data = {"relay_light_enable": 3}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    # Patch LIGHT_DEFINITIONS for this test
    from custom_components.vistapool import light as light_module

    light_module.LIGHT_DEFINITIONS["Test Light"] = {
        "switch_type": "relay_timer",
        "icon_on": "mdi:lightbulb-on",
        "icon_off": "mdi:lightbulb-off",
    }

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    assert any(isinstance(e, VistaPoolLight) for e in entities)
    assert any(e._key == "Test Light" for e in entities)


@pytest.mark.asyncio
async def test_light_async_setup_entry_no_data(caplog):
    """Test async_setup_entry logs warning and adds no entities if no data."""

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
        assert "No data from Modbus" in caplog.text
    async_add_entities.assert_not_called()


@pytest.mark.asyncio
async def test_light_async_setup_entry_option_disabled(monkeypatch):
    """Test async_setup_entry skips light if option is False."""

    class DummyEntry:
        entry_id = "test_entry"
        options = {"test_option": False}

    class DummyCoordinator:
        data = {"relay_light_enable": 3}
        config_entry = DummyEntry()
        device_slug = "vistapool"

    hass = MagicMock()
    hass.data = {"vistapool": {"test_entry": DummyCoordinator()}}
    entry = DummyEntry()
    async_add_entities = MagicMock()

    from custom_components.vistapool import light as light_module

    light_module.LIGHT_DEFINITIONS["Test Option Light"] = {
        "switch_type": "relay_timer",
        "option": "test_option",
    }

    await async_setup_entry(hass, entry, async_add_entities)
    entities = async_add_entities.call_args[0][0]
    # Should skip entity, as option is False
    assert not any(e._key == "Test Option Light" for e in entities)


@pytest.mark.asyncio
async def test_light_async_added_to_hass_calls_super(mock_coordinator, light_props):
    """Test async_added_to_hass calls parent implementation."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    with patch(
        "custom_components.vistapool.light.VistaPoolEntity.async_added_to_hass",
        return_value=None,
    ) as parent:
        await ent.async_added_to_hass()
        parent.assert_called_once()


def test_light_is_on_non_relay_timer(mock_coordinator, light_props):
    """Test is_on returns False for non-relay_timer switch type."""
    props = {"switch_type": "other"}
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", props)
    assert ent.is_on is False


def test_light_is_on_unexpected_enable_value(mock_coordinator, light_props):
    """Test is_on returns False if relay_light_enable is not 3."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    mock_coordinator.data["relay_light_enable"] = 1  # not 3
    assert ent.is_on is False
    del mock_coordinator.data["relay_light_enable"]
    assert ent.is_on is False


def test_light_supported_color_modes(mock_coordinator, light_props):
    """Test supported_color_modes always returns {'onoff'}."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    assert ent.supported_color_modes == {"onoff"}


def test_light_color_mode(mock_coordinator, light_props):
    """Test color_mode always returns 'onoff'."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    assert ent.color_mode == "onoff"


@pytest.mark.asyncio
async def test_light_async_turn_on_no_client(mock_coordinator, light_props, caplog):
    """Test async_turn_on does nothing if coordinator has no client."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    # Ensure there is no client
    mock_coordinator.client = None
    ent.hass = None
    with caplog.at_level("ERROR"):
        await ent.async_turn_on()
        assert "Modbus client not available" in caplog.text


@pytest.mark.asyncio
async def test_light_async_turn_off_no_client(mock_coordinator, light_props, caplog):
    """Test async_turn_off does nothing if coordinator has no client."""
    ent = VistaPoolLight(mock_coordinator, "test_entry", "light", light_props)
    mock_coordinator.client = None
    ent.hass = None
    with caplog.at_level("ERROR"):
        await ent.async_turn_off()
        assert "Modbus client not available" in caplog.text
