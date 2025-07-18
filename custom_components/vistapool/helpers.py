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

"""
VistaPool Integration for Home Assistant - Helpers Module

This module contains helper functions for the VistaPool integration.
It includes functions to handle device time, prepare data for writing to the device,
and parse version information.
"""

import datetime
import homeassistant.util.dt as dt_util


# This function takes a dictionary of data and returns the device time as a datetime object
# It extracts the low and high parts of the time from the dictionary, combines them into a single timestamp,
# and converts it to a datetime object in UTC timezone
def get_device_time(data, hass=None) -> datetime.datetime | None:
    """Get device time and convert to datetime object."""
    low = data.get("MBF_PAR_TIME_LOW")
    high = data.get("MBF_PAR_TIME_HIGH")
    if low is None or high is None:
        return None
    unix_ts = (high << 16) | low
    if hass:
        local_tz = dt_util.get_time_zone(hass.config.time_zone)
        # WORKAROUND: This is the naive datetime object, without timezone info
        dt_naive = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_ts)
        dt_local = dt_naive.replace(tzinfo=local_tz)
        dt_utc = dt_local.astimezone(datetime.timezone.utc)
        return dt_utc
    else:
        return datetime.datetime.fromtimestamp(unix_ts, tz=datetime.timezone.utc)


# This function prepares the device time for writing to the device
# It takes the current time in the local timezone and converts it to a format suitable for the device
def prepare_device_time(hass=None) -> list[int, int]:
    """
    Prepare device time for writing to the device.
    Returns a list of two integers representing the low and high parts of the time.
    """
    if hass:
        ha_tz = dt_util.get_time_zone(hass.config.time_zone)
        now_local = datetime.datetime.now(ha_tz)
        # WORKAROUND: This is the naive datetime object, without timezone info
        epoch_local = datetime.datetime(1970, 1, 1, tzinfo=ha_tz)
        unix_time_local = int((now_local - epoch_local).total_seconds())
    else:
        unix_time_local = int(datetime.datetime.now().timestamp())
    low = unix_time_local & 0xFFFF
    high = (unix_time_local >> 16) & 0xFFFF
    return [low, high]


def parse_version(val) -> str:
    """Parse version from integer or string."""
    if isinstance(val, int):
        major = (val >> 8) & 0xFF
        minor = val & 0xFF
        return f"{major}.{minor:02d}"
    return "?"


# This function checks if the device time is out of sync with the Home Assistant time
# It compares the device time with the current time in UTC and returns True if the difference is greater than the threshold
def is_device_time_out_of_sync(data, hass=None, threshold_seconds=60) -> bool:
    """
    Returns True if device time and HA time differ by more than threshold_seconds.
    """
    device_dt = get_device_time(data, hass)
    if device_dt is None:
        return False
    now_dt = dt_util.utcnow().replace(tzinfo=datetime.timezone.utc)
    diff = abs((device_dt - now_dt).total_seconds())
    return diff > threshold_seconds


def modbus_regs_to_ascii(regs) -> str:
    """Convert list of uint16 Modbus registers to ASCII string (ASCIIZ, max 10 chars)."""
    chars = []
    for reg in regs:
        # High byte (1st char)
        high = (reg >> 8) & 0xFF
        # Low byte (2nd char)
        low = reg & 0xFF
        if high != 0:
            chars.append(chr(high))
        else:
            break
        if low != 0:
            chars.append(chr(low))
        else:
            break
    return "".join(chars)


def modbus_regs_to_hex_string(regs) -> str:
    """Return Modbus registers as hex string."""
    if not regs or not isinstance(regs, list):
        return ""
    return "".join(f"{reg:04X}" for reg in regs)


def parse_timer_block(regs) -> dict:
    """Convert 15 Modbus registers to dict of timer params."""
    # Pads the regs list to length 15 with zeros if needed
    padded = pad_list(regs, 15)

    def u32(lsb, msb):
        return (msb << 16) | lsb

    return {
        "enable": padded[0],
        "on": u32(padded[1], padded[2]),
        "off": u32(padded[3], padded[4]),
        "period": u32(padded[5], padded[6]),
        "interval": u32(padded[7], padded[8]),
        "countdown": u32(padded[9], padded[10]),
        "function": padded[11],
        "work_time": u32(padded[13], padded[14]),
    }


def build_timer_block(data) -> list[int]:
    """Convert dict of timer params to 15 Modbus registers (all as int, never None)."""

    def safe_int(val):
        try:
            return int(val)
        except Exception:
            return 0

    def split_u32(val):
        v = safe_int(val)
        return [v & 0xFFFF, (v >> 16) & 0xFFFF]

    regs = [
        safe_int(data.get("enable", 0)),
        *split_u32(data.get("on", 0)),
        *split_u32(data.get("off", 0)),
        *split_u32(data.get("period", 0)),
        *split_u32(data.get("interval", 0)),
        *split_u32(data.get("countdown", 0)),
        safe_int(data.get("function", 0)),
        0,
        *split_u32(data.get("work_time", 0)),
    ]
    return regs


def hhmm_to_seconds(hhmm) -> int:
    """Convert HH:MM string to seconds since midnight."""
    h, m = map(int, hhmm.split(":"))
    return h * 3600 + m * 60


def seconds_to_hhmm(seconds) -> str:
    """Convert seconds since midnight to HH:MM string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


def get_timer_interval(start_sec, stop_sec) -> int:
    """Calculate interval in seconds, handle over-midnight."""
    if stop_sec >= start_sec:
        return stop_sec - start_sec
    else:
        # over-midnight
        return (86400 - start_sec) + stop_sec


def generate_time_options(step_minutes=15) -> list[str]:
    """Generate a list of HH:MM strings for every step_minutes in a day."""
    options = []
    for mins in range(0, 24 * 60, step_minutes):
        h = mins // 60
        m = mins % 60
        options.append(f"{h:02d}:{m:02d}")
    return options


def get_filtration_speed(data) -> int:
    """Get filtration speed based on relay state and configuration."""
    relay_state = data.get("MBF_RELAY_STATE", 0)
    # Filtration is off if the bit 0x0002 is not set
    if not (relay_state & 0x0002):
        return 0  # Filtration is off

    par_filtration_conf = data.get("MBF_PAR_FILTRATION_CONF", 0)
    relay_speed = (relay_state & 0x00E0) >> 5
    if relay_speed == 1:
        return 1  # Low
    elif relay_speed == 2:
        return 2  # Mid
    elif relay_speed == 4:
        return 3  # High

    conf_speed = (par_filtration_conf & 0x0070) >> 4
    if conf_speed == 0:
        return 1
    elif conf_speed == 1:
        return 2
    elif conf_speed == 2:
        return 3
    return 0


def get_filtration_pump_type(par_filtration_conf) -> int:
    """Return the type of filtration pump based on configuration."""
    pump_type = (par_filtration_conf & 0x000F) >> 0
    return pump_type  # 0 = standard, 1/2 = variable speed


def pad_list(regs, length, pad_value=0) -> list[int]:
    """Return a list padded with pad_value to desired length."""
    return regs + [pad_value] * (length - len(regs))
