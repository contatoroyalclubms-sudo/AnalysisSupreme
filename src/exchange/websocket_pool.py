"""
Pool de conexões WebSocket para alta performance
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Conexão WebSocket individual com reconexão automática"""

    def __init__(self, exchange: str, url: str, on_message: Callable):
        self.exchange = exchange
        self.url = url
        self.on_message = on_message
        self.websocket = None
        self.connected = False
        self.last_heartbeat = time.time()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    async def connect(self):
        """Conecta ao WebSocket"""
        try:
            self.websocket = await websockets.connect(
                self.url, ping_interval=20, ping_timeout=10, close_timeout=10
            )
            self.connected = True
            self.reconnect_attempts = 0
            self.last_heartbeat = time.time()
            logger.info(f"WebSocket conectado: {self.exchange}")

            asyncio.create_task(self._message_loop())

        except Exception as e:
            logger.error(f"Erro ao conectar WebSocket {self.exchange}: {e}")
            self.connected = False

    async def _message_loop(self):
        """Loop principal de recebimento de mensagens"""
        try:
            async for message in self.websocket:
                self.last_heartbeat = time.time()
                try:
                    data = json.loads(message)
                    await self.on_message(self.exchange, data)
                except json.JSONDecodeError:
                    logger.warning(
                        f"Mensagem JSON inválida de {self.exchange}: {message}"
                    )
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem de {self.exchange}: {e}")

        except ConnectionClosed:
            logger.warning(f"Conexão WebSocket fechada: {self.exchange}")
            self.connected = False
            await self._reconnect()
        except Exception as e:
            logger.error(f"Erro no loop de mensagens {self.exchange}: {e}")
            self.connected = False
            await self._reconnect()

    async def _reconnect(self):
        """Reconecta automaticamente"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(
                f"Máximo de tentativas de reconexão atingido para {self.exchange}"
            )
            return

        self.reconnect_attempts += 1
        wait_time = min(2**self.reconnect_attempts, 60)

        logger.info(
            f"Tentando reconectar {self.exchange} em {wait_time}s (tentativa {self.reconnect_attempts})"
        )
        await asyncio.sleep(wait_time)
        await self.connect()

    async def send(self, message: dict):
        """Envia mensagem via WebSocket"""
        if not self.connected or not self.websocket:
            raise Exception(f"WebSocket não conectado: {self.exchange}")

        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {self.exchange}: {e}")
            self.connected = False
            raise

    async def close(self):
        """Fecha conexão WebSocket"""
        self.connected = False
        if self.websocket:
            await self.websocket.close()


class WebSocketPool:
    """Pool de conexões WebSocket para múltiplas exchanges"""

    def __init__(self, max_connections_per_exchange: int = 5):
        self.max_connections_per_exchange = max_connections_per_exchange
        self.connections: Dict[str, List[WebSocketConnection]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.data_cache: Dict[str, Dict] = {}
        self.cache_ttl = 100

    def register_handler(self, exchange: str, handler: Callable):
        """Registra handler para mensagens de uma exchange"""
        self.message_handlers[exchange] = handler

    async def add_connection(self, exchange: str, url: str):
        """Adiciona nova conexão WebSocket"""
        if exchange not in self.connections:
            self.connections[exchange] = []

        if len(self.connections[exchange]) >= self.max_connections_per_exchange:
            logger.warning(f"Máximo de conexões atingido para {exchange}")
            return

        async def on_message(exchange_name: str, data: dict):
            cache_key = f"{exchange_name}_{data.get('symbol', 'general')}"
            self.data_cache[cache_key] = {"data": data, "timestamp": time.time() * 1000}

            if exchange_name in self.message_handlers:
                await self.message_handlers[exchange_name](data)

        connection = WebSocketConnection(exchange, url, on_message)
        await connection.connect()

        if connection.connected:
            self.connections[exchange].append(connection)
            logger.info(f"Conexão WebSocket adicionada: {exchange}")

    async def get_cached_data(
        self, exchange: str, symbol: str = None
    ) -> Optional[dict]:
        """Obtém dados do cache se ainda válidos"""
        cache_key = f"{exchange}_{symbol or 'general'}"

        if cache_key in self.data_cache:
            cached = self.data_cache[cache_key]
            age = time.time() * 1000 - cached["timestamp"]

            if age <= self.cache_ttl:
                return cached["data"]
            else:
                del self.data_cache[cache_key]

        return None

    async def send_to_exchange(self, exchange: str, message: dict):
        """Envia mensagem para exchange via WebSocket"""
        if exchange not in self.connections or not self.connections[exchange]:
            raise Exception(f"Nenhuma conexão WebSocket disponível para {exchange}")

        for connection in self.connections[exchange]:
            if connection.connected:
                await connection.send(message)
                return

        raise Exception(f"Nenhuma conexão WebSocket ativa para {exchange}")

    async def close_all(self):
        """Fecha todas as conexões WebSocket"""
        for exchange_connections in self.connections.values():
            for connection in exchange_connections:
                await connection.close()

        self.connections.clear()
        logger.info("Todas as conexões WebSocket fechadas")
