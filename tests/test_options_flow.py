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
from unittest.mock import MagicMock, AsyncMock, patch

from custom_components.vistapool.options_flow import VistaPoolOptionsFlowHandler


@pytest.mark.asyncio
async def test_options_show_form():
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    result = await flow.async_step_init(user_input=None)
    assert result["type"] == "form"
    schema = result["data_schema"]
    assert "scan_interval" in str(schema)


@pytest.mark.asyncio
async def test_options_save_options():
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    user_input = {"enable_backwash_option": True, "measure_when_filtration_off": False}
    result = await flow.async_step_init(user_input=user_input)
    assert result["type"] == "create_entry"
    assert result["data"] == user_input


@pytest.mark.asyncio
async def test_options_unlock_advanced_correct(monkeypatch):
    """Test entering correct unlock_advanced advances to advanced step."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    mock_config_entry.unique_id = "pool"
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)

    with patch("custom_components.vistapool.options_flow.date") as mock_date:
        mock_today = MagicMock()
        mock_today.year = 2025
        mock_date.today.return_value = mock_today
        user_input = {"unlock_advanced": "pool2025"}
        flow.async_step_advanced = AsyncMock(return_value="advanced_step_called")
        result = await flow.async_step_init(user_input=user_input)
        assert result == "advanced_step_called"
        flow.async_step_advanced.assert_awaited_once()


@pytest.mark.asyncio
async def test_options_unlock_advanced_wrong(monkeypatch, caplog):
    """Test entering incorrect unlock_advanced shows error and logs warning."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    mock_config_entry.unique_id = "pool"
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)

    with patch("custom_components.vistapool.options_flow.date") as mock_date:
        mock_date.today.return_value.year = 2025
        user_input = {"unlock_advanced": "wrongpassword"}
        result = await flow.async_step_init(user_input=user_input)
        # Should show error in form
        assert result["type"] == "form"
        assert "unlock_advanced" in result["errors"]
        # Should log warning
        assert "Wrong password for the advanced settings!" in caplog.text


@pytest.mark.asyncio
async def test_options_already_enabled():
    """Test already_enabled creates entry directly."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {"enable_backwash_option": True}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    user_input = {"enable_backwash_option": True}
    result = await flow.async_step_init(user_input=user_input)
    assert result["type"] == "create_entry"
    assert result["data"] == user_input


@pytest.mark.asyncio
async def test_async_step_advanced(monkeypatch):
    """Test async_step_advanced creates entry and triggers reload if changed."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {
        "use_light": False,
        "use_aux1": False,
        "use_aux2": False,
        "use_aux3": False,
        "use_aux4": False,
    }
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.loop = MagicMock()
    flow.hass.config_entries.async_reload = MagicMock()
    flow._base_options = {"use_light": False}
    user_input = {"enable_backwash_option": True, "use_light": True}  # changed value
    result = await flow.async_step_advanced(user_input=user_input)
    assert result["type"] == "create_entry"
    assert result["data"]["enable_backwash_option"] is True
    # Should call reload due to use_light change
    assert flow.hass.loop.call_soon.called


@pytest.mark.asyncio
async def test_async_step_advanced_show_form():
    """Test async_step_advanced returns a form if user_input is None."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    result = await flow.async_step_advanced(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "advanced"
    assert "data_schema" in result


@pytest.mark.asyncio
async def test_options_reload_trigger(monkeypatch):
    """Test async_step_init triggers reload when use_* options change."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {"use_light": False, "use_aux1": False}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    flow.hass = MagicMock()
    flow.hass.loop = MagicMock()
    flow.hass.config_entries.async_reload = MagicMock()
    user_input = {"use_light": True, "use_aux1": False}
    # Patch date so unlock_advanced is not used
    result = await flow.async_step_init(user_input=user_input)
    assert result["type"] == "create_entry"
    # Should trigger reload (call_soon)
    assert flow.hass.loop.call_soon.called


@pytest.mark.asyncio
async def test_async_step_init_show_form():
    """Test async_step_init returns form if user_input is None."""
    mock_config_entry = MagicMock()
    mock_config_entry.options = {}
    flow = VistaPoolOptionsFlowHandler(mock_config_entry)
    result = await flow.async_step_init(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert "data_schema" in result
