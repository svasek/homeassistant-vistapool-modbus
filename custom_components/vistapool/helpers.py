import datetime
import homeassistant.util.dt as dt_util
"""
This module contains helper functions for the VistaPool integration.
It includes functions to handle device time, prepare data for writing to the device,
and parse version information.
"""

# This function takes a dictionary of data and returns the device time as a datetime object
# It extracts the low and high parts of the time from the dictionary, combines them into a single timestamp,
# and converts it to a datetime object in UTC timezone
def get_device_time(data, hass=None):
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
def prepare_device_time(hass=None):
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

def parse_version(val):
    if isinstance(val, int):
        major = (val >> 8) & 0xFF
        minor = val & 0xFF
        return f"{major}.{minor:02d}"
    return "?"

# This function checks if the device time is out of sync with the Home Assistant time
# It compares the device time with the current time in UTC and returns True if the difference is greater than the threshold
def is_device_time_out_of_sync(data, hass=None, threshold_seconds=60):
    """
    Returns True if device time and HA time differ by more than threshold_seconds.
    """
    device_dt = get_device_time(data, hass)
    if device_dt is None:
        return False
    now_dt = dt_util.utcnow().replace(tzinfo=datetime.timezone.utc)
    diff = abs((device_dt - now_dt).total_seconds())
    return diff > threshold_seconds


def modbus_regs_to_ascii(regs):
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
    return ''.join(chars)

def modbus_regs_to_hex_string(regs):
    """Return Modbus registers as hex string, e.g. '0058 002F 4143 5011 0238 3130'."""
    if not regs or not isinstance(regs, list):
        return ""
    return " ".join(f"{reg:04X}" for reg in regs)