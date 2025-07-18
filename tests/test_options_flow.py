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
