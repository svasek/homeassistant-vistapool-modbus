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

from custom_components.vistapool.status_mask import (
    decode_hidro_status_bits,
    decode_ion_status_bits,
    decode_ph_rx_cl_cd_status_bits,
    decode_relay_state,
)


def test_decode_relay_state_basic():
    value = 0x042B
    result = decode_relay_state(value)
    assert result["pH Acid Pump"] is True
    assert result["AUX1"] is True
    assert result["Filtration high speed"] is True
    assert result["AUX2"] is False
    assert result["Filtration current speed"] == 4  # 0x042B >> 8 == 4


def test_decode_relay_state_none():
    assert decode_relay_state(None) == {}


def test_decode_ph_rx_cl_cd_status_bits_basic():
    # flow sensor problem, acid pump active, pump active
    status = 0x1808
    unit = "pH"
    result = decode_ph_rx_cl_cd_status_bits(status, unit)
    assert result["pH flow sensor problem"] is True
    assert result["pH acid pump active"] is True
    assert result["pH pump active"] is True
    assert result["pH module control status"] is False


def test_decode_ph_rx_cl_cd_status_bits_none():
    assert decode_ph_rx_cl_cd_status_bits(None, "pH") == {}


def test_decode_ion_status_bits_basic():
    # ION On Target, ION in Pol2
    status = 0x4001
    result = decode_ion_status_bits(status)
    assert result["ION On Target"] is True
    assert result["ION in Pol2"] is True
    assert result["ION in dead time"] is False


def test_decode_ion_status_bits_none():
    assert decode_ion_status_bits(None) == {}


def test_decode_hidro_status_bits_basic():
    # HIDRO On Target, HIDRO Module active, HIDRO in Pol1
    status = 0x2021
    result = decode_hidro_status_bits(status)
    assert result["HIDRO On Target"] is True
    assert result["HIDRO Module active"] is True
    assert result["HIDRO in Pol1"] is True
    assert result["Pool Cover"] is False


def test_decode_hidro_status_bits_none():
    assert decode_hidro_status_bits(None) == {}


# --- UV Lamp relay state tests ---


def test_decode_relay_state_uv_lamp_on():
    """UV Lamp is ON when the bit at (uv_relay_gpio - 1) is set."""
    # uv_relay_gpio=3 means bit 2 (0x0004) → Pool Light position
    value = 0x0004
    result = decode_relay_state(value, uv_relay_gpio=3)
    assert result["UV Lamp"] is True


def test_decode_relay_state_uv_lamp_off():
    """UV Lamp is OFF when the bit at (uv_relay_gpio - 1) is clear."""
    value = 0x0000
    result = decode_relay_state(value, uv_relay_gpio=3)
    assert result["UV Lamp"] is False


def test_decode_relay_state_uv_lamp_gpio_1():
    """UV Lamp with gpio=1 checks bit 0 (pH Acid Pump position)."""
    value = 0x0001
    result = decode_relay_state(value, uv_relay_gpio=1)
    assert result["UV Lamp"] is True
    assert result["pH Acid Pump"] is True


def test_decode_relay_state_uv_lamp_gpio_7():
    """UV Lamp with gpio=7 checks bit 6 (AUX4 position)."""
    value = 0x0040
    result = decode_relay_state(value, uv_relay_gpio=7)
    assert result["UV Lamp"] is True
    assert result["AUX4"] is True


def test_decode_relay_state_no_uv_gpio():
    """UV Lamp key is absent when uv_relay_gpio is 0 (default)."""
    value = 0x0004
    result = decode_relay_state(value)
    assert "UV Lamp" not in result


def test_decode_relay_state_uv_lamp_among_other_relays():
    """UV Lamp is decoded correctly alongside other relay bits."""
    # Filtration + AUX1 + UV on relay 5 (AUX2 position, bit 4 = 0x0010)
    value = 0x001A  # bits 1,3,4 set → Filtration, AUX1, AUX2
    result = decode_relay_state(value, uv_relay_gpio=5)
    assert result["Filtration Pump"] is True
    assert result["AUX1"] is True
    assert result["UV Lamp"] is True


def test_decode_relay_state_uv_lamp_out_of_range():
    """UV Lamp key is absent when uv_relay_gpio is out of valid range (1-7)."""
    value = 0xFFFF
    assert "UV Lamp" not in decode_relay_state(value, uv_relay_gpio=0)
    assert "UV Lamp" not in decode_relay_state(value, uv_relay_gpio=-1)
    assert "UV Lamp" not in decode_relay_state(value, uv_relay_gpio=8)
    assert "UV Lamp" not in decode_relay_state(value, uv_relay_gpio=16)
    assert "UV Lamp" not in decode_relay_state(value, uv_relay_gpio=255)
    # Boundary: 7 is valid (last relay)
    assert "UV Lamp" in decode_relay_state(value, uv_relay_gpio=7)
