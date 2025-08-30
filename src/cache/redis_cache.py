"""
Sistema de cache Redis para dados de mercado
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RedisCache:
    """Cache Redis para dados de mercado com TTL otimizado"""

    def __init__(self, config):
        self.config = config
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}

        self.ttl_config = {
            "ticker": 100,
            "orderbook": 50,
            "trades": 200,
            "ohlcv": 1000,
            "balance": 5000,
            "orders": 1000,
            "sentiment": 3600000,  # 1 hora para sentimento
            "signals": 30000,  # 30 segundos para sinais técnicos
            "ml_predictions": 300000,  # 5 minutos para predições ML
            "market_data": 60000,  # 1 minuto para dados de mercado
        }

    async def initialize(self):
        """Inicializa conexão Redis"""
        try:
            import redis.asyncio as redis

            self.redis_client = redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            await self.redis_client.ping()
            logger.info("Cache Redis inicializado com sucesso")

        except ImportError:
            logger.warning("Redis não disponível, usando cache local")
            self.redis_client = None
        except Exception as e:
            logger.warning(f"Erro ao conectar Redis: {e}, usando cache local")
            self.redis_client = None

    async def get(self, key: str, data_type: str = "general") -> Optional[Any]:
        """Obtém valor do cache"""
        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)

            if key in self.local_cache:
                cached_item = self.local_cache[key]
                ttl = self.ttl_config.get(data_type, 1000)

                if time.time() * 1000 - cached_item["timestamp"] <= ttl:
                    self.cache_stats["hits"] += 1
                    return cached_item["data"]
                else:
                    del self.local_cache[key]

            self.cache_stats["misses"] += 1
            return None

        except Exception as e:
            logger.error(f"Erro ao obter do cache: {e}")
            self.cache_stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, data_type: str = "general"):
        """Define valor no cache"""
        try:
            ttl_ms = self.ttl_config.get(data_type, 1000)
            ttl_seconds = max(1, ttl_ms // 1000)

            if self.redis_client:
                await self.redis_client.setex(
                    key, ttl_seconds, json.dumps(value, default=str)
                )

            self.local_cache[key] = {"data": value, "timestamp": time.time() * 1000}

            self.cache_stats["sets"] += 1

        except Exception as e:
            logger.error(f"Erro ao definir no cache: {e}")

    async def delete(self, key: str):
        """Remove valor do cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)

            if key in self.local_cache:
                del self.local_cache[key]

        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {e}")

    async def clear_expired(self):
        """Limpa itens expirados do cache local"""
        current_time = time.time() * 1000
        expired_keys = []

        for key, cached_item in self.local_cache.items():
            if current_time - cached_item["timestamp"] > 5000:
                expired_keys.append(key)

        for key in expired_keys:
            del self.local_cache[key]

        if expired_keys:
            logger.debug(f"Removidos {len(expired_keys)} itens expirados do cache")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            (self.cache_stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "hit_rate": f"{hit_rate:.1f}%",
            "local_cache_size": len(self.local_cache),
            "redis_available": self.redis_client is not None,
        }

    async def get_cached_or_compute(
        self, cache_key: str, compute_func, *args, data_type: str = "general", **kwargs
    ):
        """Obtém valor do cache ou computa se não existir"""
        try:
            cached_value = await self.get(cache_key, data_type)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            logger.debug(f"Cache miss for key: {cache_key}, computing...")
            computed_value = (
                await compute_func(*args, **kwargs)
                if asyncio.iscoroutinefunction(compute_func)
                else compute_func(*args, **kwargs)
            )

            await self.set(cache_key, computed_value, data_type)

            return computed_value

        except Exception as e:
            logger.error(f"Erro em get_cached_or_compute: {e}")
            return (
                await compute_func(*args, **kwargs)
                if asyncio.iscoroutinefunction(compute_func)
                else compute_func(*args, **kwargs)
            )

    async def close(self):
        """Fecha conexão Redis"""
        if self.redis_client:
            await self.redis_client.close()
