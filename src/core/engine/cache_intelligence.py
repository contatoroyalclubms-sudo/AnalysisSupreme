"""
Cache Intelligence - Sistema de cache multi-layer supremo
Cache inteligente com predição e otimização automática
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass, field
from collections import defaultdict
import pickle  # nosec
import lz4.frame

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache inteligente"""

    key: str
    data: Any
    timestamp: float
    ttl_ms: int
    access_count: int = 0
    last_access: float = 0.0
    size_bytes: int = 0
    compression_ratio: float = 1.0
    prediction_score: float = 0.0

    @property
    def age_ms(self) -> float:
        """Idade da entrada em milissegundos"""
        return (time.time() * 1000) - self.timestamp

    @property
    def is_expired(self) -> bool:
        """Verifica se entrada expirou"""
        return self.age_ms > self.ttl_ms

    @property
    def access_frequency(self) -> float:
        """Frequência de acesso por minuto"""
        age_minutes = self.age_ms / (1000 * 60)
        return self.access_count / max(age_minutes, 0.1)


class CacheIntelligence:
    """Sistema de cache inteligente multi-layer"""

    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0

        self.l1_cache: Dict[str, CacheEntry] = {}  # Ultra rápido - 10ms TTL
        self.l2_cache: Dict[str, CacheEntry] = {}  # Rápido - 100ms TTL
        self.l3_cache: Dict[str, CacheEntry] = {}  # Normal - 1s TTL
        self.l4_cache: Dict[str, CacheEntry] = {}  # Longo prazo - 10s TTL

        self.ttl_config = {
            "ticker": {"l1": 10, "l2": 50, "l3": 200, "l4": 1000},
            "orderbook": {"l1": 5, "l2": 25, "l3": 100, "l4": 500},
            "trades": {"l1": 20, "l2": 100, "l3": 500, "l4": 2000},
            "ohlcv": {"l1": 100, "l2": 500, "l3": 2000, "l4": 10000},
            "balance": {"l1": 1000, "l2": 5000, "l3": 10000, "l4": 30000},
            "signals": {"l1": 50, "l2": 200, "l3": 1000, "l4": 5000},
        }

        self.access_patterns: Dict[str, List[float]] = defaultdict(list)
        self.hit_rates: Dict[str, float] = defaultdict(float)
        self.prediction_accuracy = 0.0

        self.prediction_model: Dict[str, Any] = {}
        self.access_history: Dict[str, List[float]] = defaultdict(list)

        self.compression_threshold = 1024  # 1KB
        self.compression_stats: Dict[str, int] = defaultdict(int)

        self.optimization_interval = 60  # 60s
        self.last_optimization = time.time()

    async def initialize_intelligence(self):
        """Inicializa sistema de cache inteligente"""
        logger.info("🧠 Inicializando Cache Intelligence")

        asyncio.create_task(self._auto_optimizer())
        asyncio.create_task(self._prediction_trainer())
        asyncio.create_task(self._memory_manager())

        logger.info("✅ Cache Intelligence inicializado")

    async def get_intelligent(
        self, key: str, data_type: str = "general"
    ) -> Optional[Any]:
        """Obtém dados com inteligência multi-layer"""
        start_time = time.time() * 1000

        self.access_history[key].append(start_time)

        for layer_name, cache_layer in [
            ("L1", self.l1_cache),
            ("L2", self.l2_cache),
            ("L3", self.l3_cache),
            ("L4", self.l4_cache),
        ]:
            if key in cache_layer:
                entry = cache_layer[key]

                if not entry.is_expired:
                    entry.access_count += 1
                    entry.last_access = start_time

                    self.hit_rates[layer_name] += 0.1

                    await self._promote_entry(key, entry, layer_name)

                    logger.debug(f"🎯 Cache hit {layer_name}: {key}")
                    return entry.data
                else:
                    await self._remove_entry(key, cache_layer)

        logger.debug(f"❌ Cache miss: {key}")
        return None

    async def set_intelligent(self, key: str, data: Any, data_type: str = "general"):
        """Define dados com inteligência de placement"""
        current_time = time.time() * 1000

        data_size = self._calculate_size(data)

        compressed_data, compression_ratio = await self._compress_if_needed(
            data, data_size
        )

        best_layer = await self._determine_best_layer(key, data_type)

        ttl_ms = self.ttl_config.get(data_type, {}).get(best_layer.lower(), 1000)

        entry = CacheEntry(
            key=key,
            data=compressed_data,
            timestamp=current_time,
            ttl_ms=ttl_ms,
            size_bytes=data_size,
            compression_ratio=compression_ratio,
            prediction_score=await self._calculate_prediction_score(key),
        )

        cache_layer = getattr(self, f"{best_layer.lower()}_cache")
        cache_layer[key] = entry

        self.current_memory_bytes += data_size

        if self.current_memory_bytes > self.max_memory_bytes:
            await self._intelligent_eviction()

        logger.debug(f"💾 Cache set {best_layer}: {key} ({data_size} bytes)")

    async def _determine_best_layer(self, key: str, data_type: str) -> str:
        """Determina melhor layer baseado em inteligência"""
        access_history = self.access_history.get(key, [])

        if len(access_history) < 2:
            return "L2"

        recent_accesses = [
            a for a in access_history if (time.time() * 1000 - a) < 60000
        ]  # Último minuto
        access_frequency = len(recent_accesses)

        if access_frequency > 10:
            return "L1"  # Muito frequente
        elif access_frequency > 5:
            return "L2"  # Frequente
        elif access_frequency > 1:
            return "L3"  # Moderado
        else:
            return "L4"  # Pouco frequente

    async def _promote_entry(self, key: str, entry: CacheEntry, current_layer: str):
        """Promove entrada para layer superior se muito acessada"""
        if entry.access_frequency > 5 and current_layer != "L1":
            target_layer = {"L4": "L3", "L3": "L2", "L2": "L1"}.get(current_layer)

            if target_layer:
                current_cache = getattr(self, f"{current_layer.lower()}_cache")
                target_cache = getattr(self, f"{target_layer.lower()}_cache")

                del current_cache[key]
                target_cache[key] = entry

                logger.debug(
                    f"⬆️  Promovido {key} de {current_layer} para {target_layer}"
                )

    async def _compress_if_needed(self, data: Any, size: int) -> Tuple[Any, float]:
        """Comprime dados se necessário"""
        if size < self.compression_threshold:
            return data, 1.0

        try:
            serialized = pickle.dumps(data)

            compressed = lz4.frame.compress(serialized)

            compression_ratio = len(serialized) / len(compressed)

            if compression_ratio > 1.2:  # Pelo menos 20% de economia
                self.compression_stats["compressed"] += 1
                return compressed, compression_ratio
            else:
                self.compression_stats["not_compressed"] += 1
                return data, 1.0

        except Exception as e:
            logger.warning(f"⚠️  Erro na compressão: {e}")
            return data, 1.0

    def _calculate_size(self, data: Any) -> int:
        """Calcula tamanho dos dados"""
        try:
            if isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, dict):
                return len(json.dumps(data, default=str))
            else:
                return len(pickle.dumps(data))
        except:
            return 1024  # Estimativa padrão

    async def _calculate_prediction_score(self, key: str) -> float:
        """Calcula score de predição para o item"""
        access_history = self.access_history.get(key, [])

        if len(access_history) < 3:
            return 0.5  # Score neutro

        intervals = []
        for i in range(1, len(access_history)):
            interval = access_history[i] - access_history[i - 1]
            intervals.append(interval)

        if not intervals:
            return 0.5

        avg_interval = sum(intervals) / len(intervals)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)

        regularity_score = 1.0 / (1.0 + variance / (avg_interval**2))

        return min(1.0, regularity_score)

    async def _intelligent_eviction(self):
        """Remoção inteligente de itens do cache"""
        logger.info("🧹 Iniciando limpeza inteligente do cache")

        all_entries = []

        for layer_name, cache_layer in [
            ("l4", self.l4_cache),
            ("l3", self.l3_cache),
            ("l2", self.l2_cache),
            ("l1", self.l1_cache),
        ]:
            for key, entry in cache_layer.items():
                removal_score = (
                    entry.access_frequency * 0.4
                    + entry.prediction_score * 0.3
                    + (1.0 - entry.age_ms / entry.ttl_ms) * 0.3
                )

                all_entries.append((removal_score, key, layer_name, entry))

        all_entries.sort(key=lambda x: x[0])

        target_reduction = self.max_memory_bytes * 0.25
        freed_memory = 0

        for score, key, layer_name, entry in all_entries:
            if freed_memory >= target_reduction:
                break

            cache_layer = getattr(self, f"{layer_name}_cache")
            await self._remove_entry(key, cache_layer)
            freed_memory += entry.size_bytes

        logger.info(
            f"✅ Limpeza concluída: {freed_memory / 1024 / 1024:.1f}MB liberados"
        )

    async def _remove_entry(self, key: str, cache_layer: Dict):
        """Remove entrada do cache"""
        if key in cache_layer:
            entry = cache_layer[key]
            self.current_memory_bytes -= entry.size_bytes
            del cache_layer[key]

    async def _auto_optimizer(self):
        """Otimizador automático do cache"""
        while True:
            try:
                await asyncio.sleep(self.optimization_interval)

                await self._analyze_access_patterns()

                await self._optimize_ttls()

                await self._cleanup_expired()

                logger.debug("🔧 Otimização automática do cache concluída")

            except Exception as e:
                logger.error(f"❌ Erro na otimização automática: {e}")

    async def _analyze_access_patterns(self):
        """Analisa padrões de acesso para otimização"""
        current_time = time.time() * 1000

        for key, accesses in self.access_history.items():
            recent_accesses = [a for a in accesses if current_time - a < 600000]
            self.access_history[key] = recent_accesses

    async def _optimize_ttls(self):
        """Otimiza TTLs baseado em padrões de uso"""
        for layer_name in ["L1", "L2", "L3", "L4"]:
            hit_rate = self.hit_rates.get(layer_name, 0)

            if hit_rate > 80:
                for data_type in self.ttl_config:
                    current_ttl = self.ttl_config[data_type][layer_name.lower()]
                    self.ttl_config[data_type][layer_name.lower()] = min(
                        current_ttl * 1.1, current_ttl * 2
                    )
            elif hit_rate < 30:
                for data_type in self.ttl_config:
                    current_ttl = self.ttl_config[data_type][layer_name.lower()]
                    self.ttl_config[data_type][layer_name.lower()] = max(
                        current_ttl * 0.9, current_ttl * 0.5
                    )

    async def _cleanup_expired(self):
        """Limpa entradas expiradas"""
        for layer_name, cache_layer in [
            ("l1", self.l1_cache),
            ("l2", self.l2_cache),
            ("l3", self.l3_cache),
            ("l4", self.l4_cache),
        ]:
            expired_keys = []
            for key, entry in cache_layer.items():
                if entry.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                await self._remove_entry(key, cache_layer)

    async def _prediction_trainer(self):
        """Treina modelo de predição de acesso"""
        while True:
            try:
                await asyncio.sleep(300)  # A cada 5 minutos

                await self._train_access_prediction()

            except Exception as e:
                logger.error(f"❌ Erro no treinamento de predição: {e}")

    async def _train_access_prediction(self):
        """Treina predição de acessos"""
        for key, accesses in self.access_history.items():
            if len(accesses) > 5:
                intervals = []
                for i in range(1, len(accesses)):
                    intervals.append(accesses[i] - accesses[i - 1])

                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    self.prediction_model[key] = {
                        "avg_interval": avg_interval,
                        "last_access": accesses[-1],
                        "confidence": min(1.0, len(accesses) / 10),
                    }

    async def _memory_manager(self):
        """Gerenciador de memória inteligente"""
        while True:
            try:
                await asyncio.sleep(30)  # A cada 30s

                memory_usage_pct = (
                    self.current_memory_bytes / self.max_memory_bytes
                ) * 100

                if memory_usage_pct > 80:
                    logger.warning(f"⚠️  Uso de memória alto: {memory_usage_pct:.1f}%")
                    await self._intelligent_eviction()

            except Exception as e:
                logger.error(f"❌ Erro no gerenciador de memória: {e}")

    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Estatísticas do cache inteligente"""
        total_entries = (
            len(self.l1_cache)
            + len(self.l2_cache)
            + len(self.l3_cache)
            + len(self.l4_cache)
        )

        memory_usage_pct = (self.current_memory_bytes / self.max_memory_bytes) * 100

        return {
            "total_entries": total_entries,
            "memory_usage_mb": round(self.current_memory_bytes / 1024 / 1024, 2),
            "memory_usage_pct": round(memory_usage_pct, 1),
            "layer_distribution": {
                "L1": len(self.l1_cache),
                "L2": len(self.l2_cache),
                "L3": len(self.l3_cache),
                "L4": len(self.l4_cache),
            },
            "hit_rates": dict(self.hit_rates),
            "compression_stats": dict(self.compression_stats),
            "prediction_model_size": len(self.prediction_model),
            "access_patterns_tracked": len(self.access_history),
        }

    async def shutdown_intelligence(self):
        """Finaliza cache inteligente"""
        logger.info("🛑 Finalizando Cache Intelligence...")

        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l3_cache.clear()
        self.l4_cache.clear()

        self.access_patterns.clear()
        self.access_history.clear()
        self.prediction_model.clear()

        self.current_memory_bytes = 0

        logger.info("✅ Cache Intelligence finalizado")

    def get_stats(self) -> Dict[str, Any]:
        """Alias para compatibilidade - retorna estatísticas do cache"""
        return self.get_intelligence_stats()


cache_intelligence = CacheIntelligence()
