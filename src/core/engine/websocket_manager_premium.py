"""
WebSocket Manager Premium - Conexões ultra otimizadas
Sistema supremo de WebSocket com latência mínima
"""

import asyncio
import json
import logging
import time
import ssl
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
import aiohttp
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PremiumConnection:
    """Conexão WebSocket premium otimizada"""

    exchange: str
    url: str
    websocket: Optional[websockets.WebSocketServerProtocol] = None
    connected: bool = False
    last_ping: float = 0.0
    last_pong: float = 0.0
    message_count: int = 0
    error_count: int = 0
    latency_samples: List[float] = field(default_factory=list)

    @property
    def avg_latency_ms(self) -> float:
        """Latência média em milissegundos"""
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

    @property
    def health_score(self) -> float:
        """Score de saúde da conexão (0-100)"""
        if not self.connected:
            return 0.0

        latency_score = max(0, 100 - (self.avg_latency_ms / 10))  # 10ms = 0 pontos
        error_score = max(0, 100 - (self.error_count * 10))
        uptime_score = 100 if self.connected else 0

        return (latency_score + error_score + uptime_score) / 3


class WebSocketManagerPremium:
    """Manager premium de WebSocket com otimizações extremas"""

    def __init__(self, max_connections_per_exchange: int = 10):
        self.max_connections_per_exchange = max_connections_per_exchange
        self.connections: Dict[str, List[PremiumConnection]] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.data_cache: Dict[str, Any] = {}

        self.ssl_context = self._create_optimized_ssl_context()
        self.connection_pool = None

        self.total_messages = 0
        self.total_reconnections = 0
        self.avg_latency_ms = 0.0

        self.connection_weights: Dict[str, Dict[int, float]] = {}

        self.ultra_cache = {}
        self.cache_ttl_ms = 50  # 50ms TTL ultra baixo

    def _create_optimized_ssl_context(self) -> ssl.SSLContext:
        """Cria contexto SSL otimizado para performance"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        context.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        )
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1

        return context

    async def initialize_premium(self):
        """Inicializa o manager premium"""
        logger.info("🚀 Inicializando WebSocket Manager Premium")

        if not self.connection_pool:
            self.connection_pool = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

        premium_urls = {
            "binance": [
                "wss://stream.binance.com:443/ws/btcusdt@ticker",
                "wss://stream.binance.com:443/ws/btcusdt@depth5@100ms",
                "wss://stream.binance.com:443/ws/btcusdt@trade",
            ],
            "bybit": [
                "wss://stream.bybit.com/v5/public/spot",
                "wss://stream-testnet.bybit.com/v5/public/spot",
            ],
            "okx": [
                "wss://ws.okx.com:8443/ws/v5/public",
                "wss://wsaws.okx.com:8443/ws/v5/public",
            ],
        }

        for exchange, urls in premium_urls.items():
            await self._create_premium_connections(exchange, urls)

        asyncio.create_task(self._health_monitor())

        logger.info(
            f"✅ WebSocket Manager Premium inicializado com {self._total_connections()} conexões"
        )

    async def _create_premium_connections(self, exchange: str, urls: List[str]):
        """Cria conexões premium para uma exchange"""
        if exchange not in self.connections:
            self.connections[exchange] = []
            self.connection_weights[exchange] = {}

        for i, url in enumerate(urls[: self.max_connections_per_exchange]):
            try:
                connection = PremiumConnection(exchange=exchange, url=url)
                await self._connect_premium(connection)

                if connection.connected:
                    self.connections[exchange].append(connection)
                    self.connection_weights[exchange][i] = 1.0

                    asyncio.create_task(
                        self._premium_message_loop(connection),
                        name=f"premium_loop_{exchange}_{i}",
                    )

                    logger.info(f"✅ Conexão premium criada: {exchange} #{i}")

            except Exception as e:
                logger.error(f"❌ Erro criando conexão premium {exchange}: {e}")

    async def _connect_premium(self, connection: PremiumConnection):
        """Conecta com otimizações premium"""
        try:
            extra_headers = {
                "User-Agent": "AnalysisSupreme-Premium/1.0",
                "Connection": "Upgrade",
                "Upgrade": "websocket",
            }

            connection.websocket = await websockets.connect(
                connection.url,
                ssl=self.ssl_context,
                extra_headers=extra_headers,
                ping_interval=10,  # Ping mais frequente
                ping_timeout=5,  # Timeout menor
                close_timeout=3,  # Close timeout menor
                max_size=2**20,  # 1MB max message
                max_queue=100,  # Queue menor para baixa latência
                compression=None,  # Sem compressão para velocidade
            )

            connection.connected = True
            connection.last_ping = time.time()

        except Exception as e:
            logger.error(f"❌ Erro conectando premium {connection.exchange}: {e}")
            connection.connected = False

    async def _premium_message_loop(self, connection: PremiumConnection):
        """Loop premium de mensagens com latência mínima"""
        while connection.connected:
            try:
                message = await asyncio.wait_for(
                    connection.websocket.recv(), timeout=0.1
                )  # 100ms timeout

                receive_time = time.time() * 1000

                await self._process_premium_message(connection, message, receive_time)

                connection.message_count += 1
                self.total_messages += 1

            except asyncio.TimeoutError:
                continue
            except ConnectionClosed:
                logger.warning(f"🔌 Conexão fechada: {connection.exchange}")
                connection.connected = False
                await self._reconnect_premium(connection)
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop premium {connection.exchange}: {e}")
                connection.error_count += 1

                if connection.error_count > 10:
                    connection.connected = False
                    await self._reconnect_premium(connection)
                    break

                await asyncio.sleep(0.001)  # 1ms recovery

    async def _process_premium_message(
        self, connection: PremiumConnection, message: str, receive_time: float
    ):
        """Processamento premium de mensagem"""
        try:
            data = json.loads(message)

            if "E" in data:  # Binance event time
                event_time = data["E"]
                latency = receive_time - event_time
                connection.latency_samples.append(latency)

                if len(connection.latency_samples) > 100:
                    connection.latency_samples = connection.latency_samples[-100:]

            cache_key = self._generate_cache_key(connection.exchange, data)
            self.ultra_cache[cache_key] = {
                "data": data,
                "timestamp": receive_time,
                "latency": connection.avg_latency_ms,
            }

            if connection.exchange in self.message_handlers:
                for handler in self.message_handlers[connection.exchange]:
                    try:
                        await handler(connection.exchange, data)
                    except Exception as e:
                        logger.error(f"❌ Erro no handler {connection.exchange}: {e}")

        except json.JSONDecodeError:
            logger.warning(f"⚠️  JSON inválido de {connection.exchange}")
        except Exception as e:
            logger.error(f"❌ Erro processando mensagem premium: {e}")

    def _generate_cache_key(self, exchange: str, data: Dict) -> str:
        """Gera chave de cache otimizada"""
        if "s" in data:  # Symbol
            return f"{exchange}_{data['s']}_ticker"
        elif "stream" in data:
            return f"{exchange}_{data['stream']}"
        else:
            return f"{exchange}_general_{int(time.time() * 1000)}"

    async def _reconnect_premium(self, connection: PremiumConnection):
        """Reconexão premium com backoff inteligente"""
        self.total_reconnections += 1

        base_delay = 1.0
        health_factor = (100 - connection.health_score) / 100
        delay = base_delay * (1 + health_factor * 5)  # Max 6s delay

        logger.info(f"🔄 Reconectando {connection.exchange} em {delay:.1f}s")
        await asyncio.sleep(delay)

        try:
            await self._connect_premium(connection)
            if connection.connected:
                logger.info(f"✅ Reconexão premium bem-sucedida: {connection.exchange}")
                asyncio.create_task(self._premium_message_loop(connection))
        except Exception as e:
            logger.error(f"❌ Falha na reconexão premium {connection.exchange}: {e}")

    async def _health_monitor(self):
        """Monitor de saúde das conexões premium"""
        while True:
            try:
                await asyncio.sleep(30)  # Check a cada 30s

                for exchange, connections in self.connections.items():
                    healthy_connections = 0
                    total_latency = 0

                    for i, conn in enumerate(connections):
                        health = conn.health_score

                        if health > 70:
                            healthy_connections += 1
                            self.connection_weights[exchange][i] = health / 100
                        else:
                            self.connection_weights[exchange][i] = 0.1
                            logger.warning(
                                f"⚠️  Conexão {exchange} #{i} com baixa saúde: {health:.1f}"
                            )

                        total_latency += conn.avg_latency_ms

                    if connections:
                        avg_latency = total_latency / len(connections)
                        logger.info(
                            f"📊 {exchange}: {healthy_connections}/{len(connections)} saudáveis, "
                            f"latência média: {avg_latency:.2f}ms"
                        )

            except Exception as e:
                logger.error(f"❌ Erro no monitor de saúde: {e}")

    def register_premium_handler(self, exchange: str, handler: Callable):
        """Registra handler premium para mensagens"""
        if exchange not in self.message_handlers:
            self.message_handlers[exchange] = []

        self.message_handlers[exchange].append(handler)
        logger.info(f"✅ Handler premium registrado para {exchange}")

    async def get_ultra_fast_data(
        self, exchange: str, data_type: str
    ) -> Optional[Dict]:
        """Obtém dados com latência ultra baixa"""
        current_time = time.time() * 1000

        for key, cached in self.ultra_cache.items():
            if (
                key.startswith(f"{exchange}_")
                and data_type in key
                and current_time - cached["timestamp"] <= self.cache_ttl_ms
            ):
                return cached["data"]

        return None

    def get_best_connection(self, exchange: str) -> Optional[PremiumConnection]:
        """Obtém melhor conexão baseada em load balancing"""
        if exchange not in self.connections:
            return None

        connections = self.connections[exchange]
        weights = self.connection_weights.get(exchange, {})

        best_connection = None
        best_weight = 0

        for i, conn in enumerate(connections):
            if conn.connected and weights.get(i, 0) > best_weight:
                best_weight = weights[i]
                best_connection = conn

        return best_connection

    def _total_connections(self) -> int:
        """Total de conexões ativas"""
        return sum(len(conns) for conns in self.connections.values())

    def get_premium_stats(self) -> Dict[str, Any]:
        """Estatísticas premium do manager"""
        total_connections = self._total_connections()
        healthy_connections = 0
        total_latency = 0

        for connections in self.connections.values():
            for conn in connections:
                if conn.health_score > 70:
                    healthy_connections += 1
                total_latency += conn.avg_latency_ms

        avg_latency = total_latency / total_connections if total_connections > 0 else 0

        return {
            "total_connections": total_connections,
            "healthy_connections": healthy_connections,
            "health_rate_pct": (
                (healthy_connections / total_connections * 100)
                if total_connections > 0
                else 0
            ),
            "avg_latency_ms": round(avg_latency, 2),
            "total_messages": self.total_messages,
            "total_reconnections": self.total_reconnections,
            "cache_size": len(self.ultra_cache),
            "exchanges": list(self.connections.keys()),
        }

    async def shutdown_premium(self):
        """Finaliza manager premium"""
        logger.info("🛑 Finalizando WebSocket Manager Premium...")

        for connections in self.connections.values():
            for conn in connections:
                if conn.websocket and conn.connected:
                    await conn.websocket.close()
                conn.connected = False

        if self.connection_pool:
            await self.connection_pool.close()

        self.ultra_cache.clear()
        self.data_cache.clear()

        logger.info("✅ WebSocket Manager Premium finalizado")
