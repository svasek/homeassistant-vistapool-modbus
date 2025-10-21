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

import pytest, datetime
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
    get_device_time,
    generate_time_options,
    parse_timer_block,
    modbus_regs_to_hex_string,
    is_device_time_out_of_sync,
    get_timer_interval,
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


def test_get_filtration_speed_low():
    d = {"MBF_RELAY_STATE": 0x0042, "MBF_PAR_FILTRATION_CONF": 0x0000}
    # relay_speed == 2 → Mid
    assert get_filtration_speed(d) == 2


def test_get_filtration_speed_high():
    d = {"MBF_RELAY_STATE": 0x0082, "MBF_PAR_FILTRATION_CONF": 0x0000}
    # relay_speed == 4 → High
    assert get_filtration_speed(d) == 3


def test_get_filtration_speed_conf_speed_0():
    d = {"MBF_RELAY_STATE": 0x0002, "MBF_PAR_FILTRATION_CONF": 0x0000}
    assert get_filtration_speed(d) == 1


def test_get_filtration_speed_conf_speed_1():
    d = {"MBF_RELAY_STATE": 0x0002, "MBF_PAR_FILTRATION_CONF": 0x0010}
    assert get_filtration_speed(d) == 2


def test_get_filtration_speed_conf_speed_2():
    d = {"MBF_RELAY_STATE": 0x0002, "MBF_PAR_FILTRATION_CONF": 0x0020}
    assert get_filtration_speed(d) == 3


def test_get_filtration_speed_relay_speed_1():
    d = {"MBF_RELAY_STATE": 0x0022, "MBF_PAR_FILTRATION_CONF": 0x0000}
    # relay_speed == 1, should return 1 (Low)
    assert get_filtration_speed(d) == 1


def test_get_filtration_speed_no_match():
    d = {"MBF_RELAY_STATE": 0x0002, "MBF_PAR_FILTRATION_CONF": 0x00F0}
    # relay_speed == 0, conf_speed == 15 (not 0,1,2) → default 0
    assert get_filtration_speed(d) == 0


def test_get_filtration_speed_none():
    # Empty dict, relay_state=0, should return 0 (filtration is off)
    assert get_filtration_speed({}) == 0


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


def test_parse_version_with_zero():
    assert parse_version(0x0000) == "0.00"


def test_modbus_regs_to_ascii_empty():
    assert modbus_regs_to_ascii([]) == ""


def test_build_timer_block_with_missing_keys():
    # Missing work_time, function, etc.
    data = {"enable": 1, "on": 0, "off": 0}
    regs = build_timer_block(data)
    assert len(regs) == 15


def test_get_device_time_utc():
    """Test get_device_time returns correct UTC datetime."""
    # Example: 0x0001_0002 → timestamp = (high << 16) | low
    data = {"MBF_PAR_TIME_LOW": 0x5678, "MBF_PAR_TIME_HIGH": 0x1234}
    ts = (0x1234 << 16) | 0x5678
    expected = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    dt = get_device_time(data)
    assert dt == expected


def test_get_device_time_missing_keys():
    """Test get_device_time returns None if missing data."""
    assert get_device_time({}) is None
    assert get_device_time({"MBF_PAR_TIME_LOW": 1}) is None
    assert get_device_time({"MBF_PAR_TIME_HIGH": 1}) is None


def test_get_device_time_epoch_zero():
    """Test get_device_time returns 1970-01-01T00:00:00Z for zero."""
    data = {"MBF_PAR_TIME_LOW": 0, "MBF_PAR_TIME_HIGH": 0}
    dt = get_device_time(data)
    assert dt == datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def test_get_device_time_with_hass(monkeypatch):
    """Test get_device_time returns UTC even with hass object."""

    # Prepare a dummy hass with config.time_zone
    class DummyConfig:
        time_zone = "Europe/Prague"

    class DummyHass:
        config = DummyConfig()

    # Patch dt_util.get_time_zone to always return UTC for test simplicity
    import homeassistant.util.dt as dt_util

    monkeypatch.setattr(dt_util, "get_time_zone", lambda tz: datetime.timezone.utc)

    ts = 1234567890
    data = {"MBF_PAR_TIME_LOW": ts & 0xFFFF, "MBF_PAR_TIME_HIGH": (ts >> 16) & 0xFFFF}
    dt = get_device_time(data, DummyHass())
    expected = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    assert dt == expected


def test_generate_time_options_default():
    """Test generate_time_options produces every 15 min option in a day."""
    opts = generate_time_options()
    assert len(opts) == 96  # 24h * 4 per hour
    assert opts[0] == "00:00"
    assert opts[-1] == "23:45"


def test_generate_time_options_step_30():
    """Test generate_time_options with 30-minute steps."""
    opts = generate_time_options(step_minutes=30)
    assert len(opts) == 48
    assert opts[0] == "00:00"
    assert opts[1] == "00:30"
    assert opts[-1] == "23:30"


def test_parse_timer_block_full():
    """Test parse_timer_block with a full list of 15 registers."""
    regs = list(range(1, 16))
    result = parse_timer_block(regs)
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "enable",
        "on",
        "off",
        "period",
        "interval",
        "countdown",
        "function",
        "work_time",
    }
    # Example: on = u32(regs[1], regs[2]) == (regs[2] << 16) | regs[1]
    assert result["enable"] == 1
    assert result["on"] == (3 << 16) | 2


def test_parse_timer_block_short():
    """Test parse_timer_block pads missing registers with zeros."""
    regs = [1, 2, 3]  # Only first three
    result = parse_timer_block(regs)
    assert result["enable"] == 1
    assert result["on"] == (3 << 16) | 2  # padded msb=3
    assert result["off"] == 0
    assert len(result) == 8


def test_modbus_regs_to_hex_string_basic():
    """Test modbus_regs_to_hex_string converts list to hex string."""
    regs = [0x1234, 0xABCD, 0x0001]
    hexstr = modbus_regs_to_hex_string(regs)
    assert hexstr == "1234ABCD0001"


def test_modbus_regs_to_hex_string_empty():
    """Test modbus_regs_to_hex_string handles empty and invalid input."""
    assert modbus_regs_to_hex_string([]) == ""
    assert modbus_regs_to_hex_string(None) == ""
    assert modbus_regs_to_hex_string("notalist") == ""


def test_is_device_time_out_of_sync_false(monkeypatch):
    """Test is_device_time_out_of_sync returns False for small delta."""
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    data = {
        "MBF_PAR_TIME_LOW": now & 0xFFFF,
        "MBF_PAR_TIME_HIGH": (now >> 16) & 0xFFFF,
    }
    monkeypatch.setattr(
        "homeassistant.util.dt.utcnow",
        lambda: datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc),
    )
    assert is_device_time_out_of_sync(data, None, threshold_seconds=60) is False


def test_is_device_time_out_of_sync_true(monkeypatch):
    """Test is_device_time_out_of_sync returns True for large delta."""
    # Device time 2 hours behind
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    device_time = now - 7200  # 2 hours ago
    data = {
        "MBF_PAR_TIME_LOW": device_time & 0xFFFF,
        "MBF_PAR_TIME_HIGH": (device_time >> 16) & 0xFFFF,
    }
    monkeypatch.setattr(
        "homeassistant.util.dt.utcnow",
        lambda: datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc),
    )
    assert is_device_time_out_of_sync(data, None, threshold_seconds=60) is True


def test_is_device_time_out_of_sync_none():
    """Test is_device_time_out_of_sync returns False if no device time."""
    assert is_device_time_out_of_sync({}, None, threshold_seconds=60) is False


def test_get_timer_interval_daytime():
    """Test get_timer_interval with stop >= start."""
    assert get_timer_interval(3600, 7200) == 3600  # 01:00 - 02:00


def test_get_timer_interval_overnight():
    """Test get_timer_interval with stop < start (over midnight)."""
    assert get_timer_interval(82800, 3600) == 3600 + (
        86400 - 82800
    )  # 23:00 - 01:00 = 2h


def test_get_timer_interval_zero():
    """Test get_timer_interval returns 0 if times are equal."""
    assert get_timer_interval(5000, 5000) == 0


def test_calculate_next_interval_time_with_hass():
    """Test calculate_next_interval_time with hass instance."""
    from datetime import datetime, timedelta
    from unittest.mock import MagicMock
    from zoneinfo import ZoneInfo
    from custom_components.vistapool.helpers import calculate_next_interval_time

    # Mock hass with Prague timezone
    mock_hass = MagicMock()
    mock_hass.config.time_zone = "Europe/Prague"

    # Calculate with 3600 seconds (1 hour)
    result = calculate_next_interval_time(3600, mock_hass)

    # Should be a datetime object
    assert isinstance(result, datetime)

    # Should have timezone information
    assert result.tzinfo is not None

    # Should have seconds set to 0 (rounded to nearest minute)
    assert result.second == 0
    assert result.microsecond == 0

    # Should be approximately 1 hour from now (allow 1 minute tolerance)
    prague_tz = ZoneInfo("Europe/Prague")
    expected_time = (datetime.now(prague_tz) + timedelta(seconds=3600)).replace(
        second=0, microsecond=0
    )
    time_diff = abs((result - expected_time).total_seconds())
    assert time_diff < 60, f"Time difference {time_diff} seconds is too large"


def test_calculate_next_interval_time_without_hass():
    """Test calculate_next_interval_time without hass (UTC fallback)."""
    from datetime import datetime, timedelta, timezone
    from custom_components.vistapool.helpers import calculate_next_interval_time

    # Calculate with 7200 seconds (2 hours), no hass
    result = calculate_next_interval_time(7200, None)

    # Should be a datetime object
    assert isinstance(result, datetime)

    # Should have timezone information (UTC)
    assert result.tzinfo is not None
    assert result.tzinfo == timezone.utc

    # Should have seconds set to 0 (rounded to nearest minute)
    assert result.second == 0
    assert result.microsecond == 0

    # Should be approximately 2 hours from now in UTC (allow 1 minute tolerance)
    expected_time = (datetime.now(timezone.utc) + timedelta(seconds=7200)).replace(
        second=0, microsecond=0
    )
    time_diff = abs((result - expected_time).total_seconds())
    assert time_diff < 60, f"Time difference {time_diff} seconds is too large"


def test_calculate_next_interval_time_zero_value():
    """Test calculate_next_interval_time returns None for zero value."""
    from custom_components.vistapool.helpers import calculate_next_interval_time

    result = calculate_next_interval_time(0, None)
    assert result is None


def test_calculate_next_interval_time_negative_value():
    """Test calculate_next_interval_time returns None for negative value."""
    from custom_components.vistapool.helpers import calculate_next_interval_time

    result = calculate_next_interval_time(-100, None)
    assert result is None


def test_calculate_next_interval_time_none_value():
    """Test calculate_next_interval_time returns None for None value."""
    from custom_components.vistapool.helpers import calculate_next_interval_time

    result = calculate_next_interval_time(None, None)
    assert result is None


def test_calculate_next_interval_time_invalid_type():
    """Test calculate_next_interval_time returns None for invalid type."""
    from custom_components.vistapool.helpers import calculate_next_interval_time

    result = calculate_next_interval_time("not a number", None)
    assert result is None
