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
from custom_components.vistapool.modbus_compat import (
    address_kwargs,
    modbus_acall,
    modbus_scall,
)


@pytest.mark.asyncio
async def test_address_kwargs_device_id():
    class Dummy:
        async def async_read_holding_registers(self, *, address, count, device_id):
            return (address, count, device_id)

    d = Dummy()
    m = d.async_read_holding_registers
    assert address_kwargs(m, 5) == {"device_id": 5}
    assert await modbus_acall(m, 5, address=0x200, count=2) == (0x200, 2, 5)


@pytest.mark.asyncio
async def test_address_kwargs_slave():
    class Dummy:
        async def async_read_holding_registers(self, *, address, count, slave):
            return (address, count, slave)

    d = Dummy()
    m = d.async_read_holding_registers
    assert address_kwargs(m, 7) == {"slave": 7}
    assert await modbus_acall(m, 7, address=0x300, count=1) == (0x300, 1, 7)


def test_scall_sync_variants():
    class D1:
        def read_coils(self, *, address, count, device_id):
            return (address, count, device_id)

    class D2:
        def read_coils(self, *, address, count, slave):
            return (address, count, slave)

    d1, d2 = D1(), D2()
    assert modbus_scall(d1.read_coils, 10, address=0x10, count=3) == (0x10, 3, 10)
    assert modbus_scall(d2.read_coils, 11, address=0x11, count=4) == (0x11, 4, 11)
