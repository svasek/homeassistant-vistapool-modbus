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
async def test_async_read_all_with_retry(config):
    """Test that async_read_all retries after one failure."""
    client = vistapool_modbus.VistaPoolModbusClient(config)
    call_count = {"count": 0}

    async def maybe_fail():
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise Exception("fail")
        return {"success": True}

    client._perform_read_all = maybe_fail
    result = await client.async_read_all()
    assert result == {"success": True}
    assert client._consecutive_errors == 0


@pytest.mark.asyncio
async def test_async_write_register_success(config):
    client = vistapool_modbus.VistaPoolModbusClient(config)
    # Mock inner method to succeed
    client._perform_write_register = AsyncMock(return_value={"result": True})
    result = await client.async_write_register(0x0100, 123)
    assert result == {"result": True}


@pytest.mark.asyncio
async def test_async_write_register_failure(config):
    client = vistapool_modbus.VistaPoolModbusClient(config)
    # Mock inner method to raise exception on first call
    client._perform_write_register = AsyncMock(side_effect=Exception("write fail"))
    with pytest.raises(Exception, match="write fail"):
        await client.async_write_register(0x0100, 123)
    # After failure, _consecutive_errors should be incremented
    assert client._consecutive_errors == 1


@pytest.mark.asyncio
async def test_write_timer_success(config):
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_timer = AsyncMock(return_value=True)
    result = await client.write_timer("filtration1", {"on": 1, "interval": 100})
    assert result is True


@pytest.mark.asyncio
async def test_write_timer_failure(config):
    client = vistapool_modbus.VistaPoolModbusClient(config)
    client._perform_write_timer = AsyncMock(side_effect=Exception("timer fail"))
    with pytest.raises(Exception, match="timer fail"):
        await client.write_timer("filtration1", {"on": 0})
    assert client._consecutive_errors == 1


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
