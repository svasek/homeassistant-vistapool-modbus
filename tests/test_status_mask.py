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
from custom_components.vistapool.status_mask import (
    decode_notification_mask,
    decode_relay_state,
    decode_ph_rx_cl_cd_status_bits,
    decode_ion_status_bits,
    decode_hidro_status_bits,
)


def test_decode_notification_mask_basic():
    # 0x003F = všechny první flags zapnuté
    result = decode_notification_mask(0x003F)
    assert result["NOTIF_IO"] is True
    assert result["NOTIF_PAGE"] is False


def test_decode_notification_mask_none():
    assert decode_notification_mask(None) == {}


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
    assert result["HIDRO Cover input active"] is False


def test_decode_hidro_status_bits_none():
    assert decode_hidro_status_bits(None) == {}
