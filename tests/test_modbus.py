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
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

import custom_components.vistapool.modbus as vistapool_modbus
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def config():
    return {"host": "127.0.0.1", "port": 502, "slave": 1}


@pytest.mark.asyncio
async def test_safe_close_client_with_none(config):
    """Test that _safe_close_client does not raise if _client is None."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    await client._safe_close_client()  # Should not raise


@pytest.mark.asyncio
async def test_establish_connection_with_retry_success(config):
    """Test successful connection establishment with retry."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    with patch.object(vistapool_modbus, "AsyncModbusTcpClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.connect = AsyncMock(return_value=True)
        mock_instance.connected = True

        result_client = await client._establish_connection_with_retry()
        assert result_client is mock_instance
        assert client._consecutive_errors == 0


@pytest.mark.asyncio
async def test_establish_connection_with_retry_failure(config):
    """Test failed connection with retries and backoff set."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    with patch.object(vistapool_modbus, "AsyncModbusTcpClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.connect = AsyncMock(side_effect=Exception("fail"))
        mock_instance.connected = False

        with pytest.raises(vistapool_modbus.ConnectionException):
            await client._establish_connection_with_retry()
        assert client._backoff_until is not None


@pytest.mark.asyncio
async def test_is_connection_healthy_recent_success(config):
    """Test connection health check with recent successful operation."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._client = AsyncMock()
    client._client.connected = True
    client._last_successful_operation = datetime.now()
    assert await client._is_connection_healthy() is True


@pytest.mark.asyncio
async def test_is_connection_healthy_healthcheck(config):
    """Test connection health check logic."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._client = AsyncMock()
    client._client.connected = True
    client._last_successful_operation = None

    # Mock successful Modbus reply
    healthy_reply = AsyncMock()
    healthy_reply.isError = lambda: False
    client._client.read_holding_registers = AsyncMock(return_value=healthy_reply)
    assert await client._is_connection_healthy() is True

    # Mock error Modbus reply
    error_reply = AsyncMock()
    error_reply.isError = lambda: True
    client._client.read_holding_registers = AsyncMock(return_value=error_reply)
    client._last_successful_operation = None  # reset!
    assert await client._is_connection_healthy() is False


@pytest.mark.asyncio
async def test_async_read_all_success(config):
    """Test async_read_all returns dict from _perform_read_all."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_read_all = AsyncMock(return_value={"data": 123})
    result = await client.async_read_all()
    assert result == {"data": 123}


@pytest.mark.asyncio
async def test_async_read_all_failure(config):
    """Test async_read_all raises if _perform_read_all fails both retries."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_read_all = AsyncMock(side_effect=Exception("read fail"))
    with pytest.raises(Exception, match="read fail"):
        await client.async_read_all()


@pytest.mark.asyncio
async def test_async_write_register_success(config):
    """Test async_write_register returns value from _perform_write_register."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_register = AsyncMock(return_value={"result": True})
    result = await client.async_write_register(0x0100, 123)
    assert result == {"result": True}


@pytest.mark.asyncio
async def test_async_write_register_failure(config):
    """Test async_write_register raises if _perform_write_register raises Exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_register = AsyncMock(side_effect=Exception("write fail"))
    with pytest.raises(Exception, match="write fail"):
        await client.async_write_register(0x0100, 123)


@pytest.mark.asyncio
async def test_write_timer_success(config):
    """Test write_timer returns True if _perform_write_timer succeeds."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_timer = AsyncMock(return_value=True)
    result = await client.write_timer("filtration1", {"on": 1, "interval": 100})
    assert result is True


@pytest.mark.asyncio
async def test_write_timer_failure(config):
    """Test write_timer raises if _perform_write_timer raises Exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_timer = AsyncMock(side_effect=Exception("timer fail"))
    with pytest.raises(Exception, match="timer fail"):
        await client.write_timer("filtration1", {"on": 0})


@pytest.mark.asyncio
async def test_async_write_aux_relay_success(config):
    """Test async_write_aux_relay returns None (success) or {} (connection error)."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_aux_relay = AsyncMock(return_value=None)
    result = await client.async_write_aux_relay(1, True)
    assert result is None or result == {}


@pytest.mark.asyncio
async def test_async_write_aux_relay_failure(config):
    """Test async_write_aux_relay returns {} if _perform_write_aux_relay raises Exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_aux_relay = AsyncMock(side_effect=Exception("aux fail"))
    result = await client.async_write_aux_relay(1, True)
    assert result == {}


@pytest.mark.asyncio
async def test_write_register_connection_lost(config):
    client = vistapool_modbus.VistaPoolModbusClient(config)
    # Simulate a ConnectionException during write
    client._perform_write_register = AsyncMock(
        side_effect=vistapool_modbus.ConnectionException("connection lost")
    )
    with pytest.raises(vistapool_modbus.ConnectionException):
        await client.async_write_register(0x0100, 456)
    assert client._consecutive_errors == 1


def test_connection_stats_content(config):
    """Test connection_stats property structure."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    stats = client.connection_stats
    assert stats["host"] == "127.0.0.1"
    assert isinstance(stats["total_operations"], int)
    assert "success_rate_percent" in stats


@pytest.mark.asyncio
async def test_perform_read_all_happy_path(config, monkeypatch):
    """Test _perform_read_all returns correct dict when all Modbus reads succeed."""

    client = vistapool_modbus.VistaPoolModbusClient(config)

    # Helper class for simulating Modbus response object
    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    # Prepare a fake Modbus client with async mocks for all register reads (in the correct order!)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Setup values for all reads in the order used in _perform_read_all:
    # rr00 (holding), rr01 (input), rr02 (holding), rr02_hidro (holding),
    # rr03 (holding), installer blocks (2x holding), rr05 (holding), rr06 (holding)
    fake_modbus.read_holding_registers = AsyncMock(
        side_effect=[
            DummyResp(
                [
                    1,
                    3,
                    1280,
                    32768,
                    88,
                    47,
                    16707,
                    20497,
                    8248,
                    12592,
                    0,
                    0,
                    0,
                    22069,
                    0,
                ]
            ),  # rr00
            DummyResp(
                [
                    23971,
                    8,
                    23971,
                    8,
                    26922,
                    0,
                    34208,
                    0,
                    0,
                    65426,
                    0,
                    0,
                    0,
                    0,
                    64136,
                    3,
                    25371,
                    4,
                    16,
                    0,
                ]
            ),  # rr02
            DummyResp([266, 10000]),  # rr02_hidro
            DummyResp(
                [2055, 10, 0, 0, 0, 0, 1000, 50, 0, 14687, 2600, 2, 1297]
            ),  # rr03
            DummyResp(list(range(1, 32))),  # installer block 1 (0x0408, 31)
            DummyResp(list(range(32, 45))),  # installer block 2 (0x0427, 13)
            DummyResp([650, 0, 750, 700, 0, 0, 700, 0, 100, 0, 0, 0, 5000, 0]),  # rr05
            DummyResp([9, 6, 25604, 5, 0, 2240, 545, 1281, 0, 0, 0, 0, 0]),  # rr06
        ]
    )
    fake_modbus.read_input_registers = AsyncMock(
        return_value=DummyResp(
            [
                0,
                0,
                820,
                709,
                0,
                0,
                140,
                50560,
                49536,
                1280,
                1280,
                0,
                8192,
                16928,
                0,
                0,
                9,
                0,
            ]
        )
    )

    # Patch get_client() to return the fake client
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    # Call the tested method
    result = await client._perform_read_all()

    # Verify key values in the result (not everything, just main signals)
    assert isinstance(result, dict)
    assert "MBF_POWER_MODULE_VERSION" in result
    assert result["MBF_POWER_MODULE_VERSION"] == 1280
    assert "MBF_MEASURE_PH" in result
    assert result["MBF_MEASURE_PH"] == 8.20
    assert "MBF_PAR_PH1" in result
    assert result["MBF_PAR_PH1"] == 7.5
    assert "FILTRATION_SPEED" in result

    # Verify that all Modbus calls were made as expected
    assert fake_modbus.read_holding_registers.await_count == 8
    assert fake_modbus.read_input_registers.await_count == 1


@pytest.mark.asyncio
async def test_read_all_timers_success(config):
    """Test read_all_timers returns dict with timers when _perform_read_all_timers succeeds."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    timers_result = {
        "filtration1": {"enable": 1, "on": 100, "interval": 3600},
        "relay_aux1": {"enable": 0, "on": 0, "interval": 0},
    }
    client._perform_read_all_timers = AsyncMock(return_value=timers_result)
    result = await client.read_all_timers()
    assert result == timers_result


@pytest.mark.asyncio
async def test_read_all_timers_exception(config):
    """Test read_all_timers raises if _perform_read_all_timers throws Exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_read_all_timers = AsyncMock(side_effect=Exception("timers fail"))
    with pytest.raises(Exception, match="timers fail"):
        await client.read_all_timers()
    assert client._consecutive_errors == 1


@pytest.mark.asyncio
async def test_read_all_timers_not_connected(config):
    """Test read_all_timers returns {} if client is not connected."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_read_all_timers = AsyncMock(return_value={})
    result = await client.read_all_timers()
    assert result == {}


@pytest.mark.asyncio
async def test_perform_read_all_timers_all_enabled(config, monkeypatch):
    """Test _perform_read_all_timers reads all timer blocks when enabled_timers is None."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Dummy response for timer blocks (always 15 registers, ascending numbers)
    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    # All timer blocks should return this
    fake_modbus.read_holding_registers = AsyncMock(
        return_value=DummyResp(list(range(15)))
    )

    # Patch get_client() to always return our fake_modbus
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    # Call the method (should read all timers in TIMER_BLOCKS)
    result = await client._perform_read_all_timers(enabled_timers=None)

    # Check that all blocks from TIMER_BLOCKS were read and returned
    from custom_components.vistapool.const import TIMER_BLOCKS

    assert set(result.keys()) == set(TIMER_BLOCKS.keys())
    for timer, data in result.items():
        assert isinstance(data, dict)
        assert "enable" in data
        assert "on" in data
        assert "interval" in data

    # Ensure correct number of calls (one per block)
    assert fake_modbus.read_holding_registers.await_count == len(TIMER_BLOCKS)


@pytest.mark.asyncio
async def test_perform_read_all_timers_only_selected(config, monkeypatch):
    """Test _perform_read_all_timers reads only selected timer blocks."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp([0] * 15))

    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    # Pick two timers only
    enabled = ["filtration1", "relay_aux1"]
    result = await client._perform_read_all_timers(enabled_timers=enabled)
    assert set(result.keys()) == set(enabled)
    assert fake_modbus.read_holding_registers.await_count == len(enabled)


@pytest.mark.asyncio
async def test_perform_read_all_timers_modbus_error(config, monkeypatch):
    """Test _perform_read_all_timers skips block if isError is True."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, is_error=True):
            self.isError = lambda: is_error
            self.registers = [0] * 15

    fake_modbus.read_holding_registers = AsyncMock(
        return_value=DummyResp(is_error=True)
    )
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    # Should return empty dict (nothing read successfully)
    result = await client._perform_read_all_timers(enabled_timers=["filtration1"])
    assert result == {}


@pytest.mark.asyncio
async def test_perform_read_all_timers_exception(config, monkeypatch):
    """Test _perform_read_all_timers skips block on exception."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Simulate an exception during register read
    fake_modbus.read_holding_registers = AsyncMock(side_effect=Exception("fail"))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_read_all_timers(enabled_timers=["relay_aux2"])
    assert result == {}


@pytest.mark.asyncio
async def test_perform_read_all_timers_not_connected(config, monkeypatch):
    """Test _perform_read_all_timers returns {} if client is not connected."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = False

    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_read_all_timers()
    assert result == {}


@pytest.mark.asyncio
async def test_perform_write_register_happy_path(config, monkeypatch):
    """Test _perform_write_register returns dict with confirmation on success."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, val, is_error=False):
            self.isError = lambda: is_error
            self.registers = [val]

    fake_modbus.write_registers = AsyncMock(return_value=DummyResp(123, False))
    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp(123, False))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_register(0x0100, 123)
    assert isinstance(result, dict)
    assert result["address"] == 0x0100
    assert result["value"] == 123
    assert result["confirmed"] == 123


@pytest.mark.asyncio
async def test_perform_write_register_write_isError(config, monkeypatch):
    """Test _perform_write_register returns None if write_registers returns error."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, val, is_error):
            self.isError = lambda: is_error
            self.registers = [val]

    fake_modbus.write_registers = AsyncMock(return_value=DummyResp(0, True))
    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp(0, False))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_register(0x0100, 123)
    assert result is None


@pytest.mark.asyncio
async def test_perform_write_register_confirm_isError(config, monkeypatch):
    """Test _perform_write_register returns None if confirm read returns error."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, val, is_error):
            self.isError = lambda: is_error
            self.registers = [val]

    fake_modbus.write_registers = AsyncMock(return_value=DummyResp(123, False))
    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp(0, True))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_register(0x0100, 123)
    assert result is None


@pytest.mark.asyncio
async def test_perform_write_register_not_connected(config, monkeypatch):
    """Test _perform_write_register returns {} if client is not connected."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = False
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))
    result = await client._perform_write_register(0x0100, 123)
    assert result == {}


@pytest.mark.asyncio
async def test_perform_write_register_exception(config, monkeypatch):
    """Test _perform_write_register returns {} if write_registers raises exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True
    fake_modbus.write_registers = AsyncMock(side_effect=Exception("modbus write fail"))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))
    result = await client._perform_write_register(0x0100, 123)
    assert result == {}


@pytest.mark.asyncio
async def test_perform_write_register_apply(config, monkeypatch):
    """Test _perform_write_register triggers EEPROM/EXEC writes when apply=True."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, is_error=False):
            self.isError = lambda: is_error
            self.registers = [1]

    fake_modbus.write_registers = AsyncMock(return_value=DummyResp(is_error=False))
    fake_modbus.read_holding_registers = AsyncMock(
        return_value=DummyResp(is_error=False)
    )
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_register(0x0100, 123, apply=True)
    # Should still succeed, as happy path
    assert result is not None
    # There should be at least 3 write_registers calls (register, EEPROM, EXEC)
    assert fake_modbus.write_registers.await_count >= 3


@pytest.mark.asyncio
async def test_perform_write_register_logs_exception(config, monkeypatch, caplog):
    """Test that _perform_write_register logs and returns {} on exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    # Simulate get_client raising
    monkeypatch.setattr(
        client, "get_client", AsyncMock(side_effect=Exception("simulated error"))
    )
    with caplog.at_level("ERROR"):
        result = await client._perform_write_register(0x0100, 123)
        assert result == {}
        assert "simulated error" in caplog.text


@pytest.mark.asyncio
async def test_perform_write_timer_happy_path(config, monkeypatch):
    """Test _perform_write_timer updates timer block and triggers EEPROM/EXEC."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Dummy response for timer block read (simulate block with 15 registers)
    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    # Patch TIMER_BLOCKS to ensure known block address
    from custom_components.vistapool.const import TIMER_BLOCKS

    block_name = "filtration1"
    block_addr = TIMER_BLOCKS[block_name]

    # Read block returns current values
    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp([0] * 15))
    # Write block, EEPROM save, EXEC all succeed
    fake_modbus.write_registers = AsyncMock(return_value=DummyResp([], False))

    # Patch get_client()
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    timer_data = {"on": 123, "interval": 321}
    result = await client._perform_write_timer(block_name, timer_data)
    assert result is True

    # Verify correct addresses used
    fake_modbus.read_holding_registers.assert_awaited_with(
        address=block_addr, count=15, slave=1
    )
    assert fake_modbus.write_registers.await_count >= 3  # timer write + eeprom + exec


@pytest.mark.asyncio
async def test_perform_write_timer_not_connected(config, monkeypatch):
    """Test _perform_write_timer returns {} if client is not connected."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = False
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_timer("filtration2", {"on": 10})
    assert result == {}


@pytest.mark.asyncio
async def test_perform_write_timer_not_connected(config, monkeypatch):
    """Test _perform_write_timer returns {} if client is not connected."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = False
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_timer("filtration2", {"on": 10})
    assert result == {}


@pytest.mark.asyncio
async def test_perform_write_timer_read_block_error(config, monkeypatch):
    """Test _perform_write_timer returns False if reading timer block fails."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, is_error=True):
            self.registers = [0] * 15
            self.isError = lambda: is_error

    fake_modbus.read_holding_registers = AsyncMock(
        return_value=DummyResp(is_error=True)
    )
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_timer("relay_aux3", {"on": 22})
    assert result is False


@pytest.mark.asyncio
async def test_perform_write_timer_write_raises(config, monkeypatch):
    """Test _perform_write_timer raises if write_registers raises exception."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    fake_modbus.read_holding_registers = AsyncMock(return_value=DummyResp([0] * 15))
    fake_modbus.write_registers = AsyncMock(side_effect=Exception("modbus write fail"))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    with pytest.raises(Exception, match="modbus write fail"):
        await client._perform_write_timer("relay_light", {"on": 1})


@pytest.mark.asyncio
async def test_perform_write_timer_write_isError(config, monkeypatch):
    """Test _perform_write_timer returns False if write_registers returns error."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, regs=None, is_error=True):
            self.registers = regs if regs is not None else [0] * 15
            self.isError = lambda: is_error

    # read_holding_registers returns ok
    fake_modbus.read_holding_registers = AsyncMock(
        return_value=DummyResp([0] * 15, is_error=False)
    )
    # write_registers returns error (for block write)
    fake_modbus.write_registers = AsyncMock(
        side_effect=[
            DummyResp([], True),  # block write returns error
            DummyResp([], False),  # eeprom save
            DummyResp([], False),  # exec
        ]
    )
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client._perform_write_timer("relay_aux4b", {"on": 10})
    assert result is False


@pytest.mark.asyncio
async def test_async_write_aux_relay_on_and_off(config, monkeypatch):
    """Test async_write_aux_relay turns AUX relay ON and OFF successfully."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Helper for simulating Modbus reply with current relay state (simulate relay is OFF)
    class DummyResp:
        def __init__(self, regs, is_error=False):
            self.registers = regs
            self.isError = lambda: is_error

    # Always return relay state 0 (all relays OFF) when reading
    fake_modbus.read_input_registers = AsyncMock(return_value=DummyResp([0]))
    # All write_registers succeed
    fake_modbus.write_registers = AsyncMock(return_value=DummyResp([], False))

    # Patch get_client() to always return fake_modbus
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    # Test turning AUX1 ON (relay_index=1, on=True)
    await client.async_write_aux_relay(1, True)
    # Test turning AUX1 OFF (relay_index=1, on=False)
    # Set initial relay state as ON (bit 0x0008 set)
    fake_modbus.read_input_registers = AsyncMock(return_value=DummyResp([0x0008]))
    await client.async_write_aux_relay(1, False)

    # Verify read and write calls for ON
    # read_input_registers should be called for 0x010E (relay state)
    fake_modbus.read_input_registers.assert_called_with(
        address=0x010E, count=1, slave=1
    )
    # write_registers is called for the sequence to update relay state and execute config
    # Order of calls: enable register, relay write, disable, execute
    assert fake_modbus.write_registers.await_count >= 4  # should be 4 per call


@pytest.mark.asyncio
async def test_async_write_aux_relay_not_connected(config, monkeypatch):
    """Test async_write_aux_relay does nothing if client is not connected."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = False

    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client.async_write_aux_relay(1, True)
    # Should log error and return empty dict
    assert result == {}


@pytest.mark.asyncio
async def test_async_write_aux_relay_read_error(config, monkeypatch):
    """Test async_write_aux_relay aborts if reading current relay state fails."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    # Simulate Modbus error
    class DummyResp:
        def __init__(self):
            self.isError = lambda: True

    fake_modbus.read_input_registers = AsyncMock(return_value=DummyResp())
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client.async_write_aux_relay(1, True)
    assert result is None or result == {}


@pytest.mark.asyncio
async def test_async_write_aux_relay_write_exception(config, monkeypatch):
    """Test async_write_aux_relay handles exception during write_registers."""

    client = vistapool_modbus.VistaPoolModbusClient(config)
    fake_modbus = AsyncMock()
    fake_modbus.connected = True

    class DummyResp:
        def __init__(self, regs):
            self.registers = regs
            self.isError = lambda: False

    # First, reading relay state works
    fake_modbus.read_input_registers = AsyncMock(return_value=DummyResp([0]))
    # write_registers throws exception
    fake_modbus.write_registers = AsyncMock(side_effect=Exception("write fail"))
    monkeypatch.setattr(client, "get_client", AsyncMock(return_value=fake_modbus))

    result = await client.async_write_aux_relay(1, True)
    assert result == {}
