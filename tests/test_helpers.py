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
from custom_components.vistapool.helpers import (
    parse_version,
    pad_list,
    modbus_regs_to_ascii,
    build_timer_block,
    get_filtration_speed,
    get_filtration_pump_type,
    hhmm_to_seconds,
    seconds_to_hhmm,
    prepare_device_time,
    parse_version,
)


def test_parse_version():
    assert parse_version(0x0123) == "1.35"
    assert parse_version("invalid") == "?"


def test_pad_list():
    assert pad_list([1, 2], 5) == [1, 2, 0, 0, 0]
    assert pad_list([], 3, pad_value=7) == [7, 7, 7]


def test_modbus_regs_to_ascii():
    assert modbus_regs_to_ascii([0x4142, 0x4300]) == "ABC"
    assert modbus_regs_to_ascii([0x4100]) == "A"


def test_build_timer_block():
    d = {"enable": 1, "on": 60, "off": 120, "function": 3, "work_time": 30}
    regs = build_timer_block(d)
    assert isinstance(regs, list) and len(regs) == 15


def test_get_filtration_speed():
    d = {"MBF_RELAY_STATE": 0x0022, "MBF_PAR_FILTRATION_CONF": 0x0070}
    assert get_filtration_speed(d) == 1


def test_get_filtration_pump_type():
    assert get_filtration_pump_type(0x0001) == 1


def test_hhmm_seconds_conversion():
    assert hhmm_to_seconds("01:30") == 5400
    assert seconds_to_hhmm(5400) == "01:30"


def test_prepare_device_time_tz():
    class DummyHass:
        class Config:
            time_zone = "Europe/Prague"

        config = Config()

    hass = DummyHass()
    result = prepare_device_time(hass)
    # Result can be either a single integer or a list of two integers
    assert isinstance(result, (int, list))
    if isinstance(result, list):
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)
    else:
        assert 0 <= result < 2400  # HHMM


def test_parse_version_invalid():
    assert parse_version(None) == "?"
    assert parse_version("not-a-number") == "?"
    assert parse_version(0xFFFF) == "255.255"
