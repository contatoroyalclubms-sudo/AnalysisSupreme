"""
Memory Optimizer - Gestão suprema de memória
Otimização extrema de uso de memória para alta performance
"""

import gc
import psutil
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import tracemalloc
import sys
import weakref
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Snapshot de uso de memória"""

    timestamp: float
    total_mb: float
    available_mb: float
    used_mb: float
    usage_pct: float
    gc_collections: Dict[int, int]
    top_allocations: List[tuple]


class MemoryOptimizer:
    """Otimizador supremo de memória"""

    def __init__(self, target_memory_mb: int = 1024):
        self.target_memory_mb = target_memory_mb
        self.target_memory_bytes = target_memory_mb * 1024 * 1024

        self.snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 100

        self.object_pools: Dict[str, List[Any]] = defaultdict(list)
        self.pool_limits = {"dict": 1000, "list": 1000, "set": 500, "tuple": 2000}

        self.weak_refs: weakref.WeakSet[Any] = weakref.WeakSet()

        self.gc_thresholds = (700, 10, 10)  # Mais agressivo
        self.cleanup_interval = 30  # 30s
        self.memory_check_interval = 10  # 10s

        self.total_cleanups = 0
        self.memory_freed_mb = 0.0
        self.gc_forced_collections = 0

        self.trace_enabled = False
        self.allocation_stats: Dict[str, int] = defaultdict(int)

    async def initialize_optimizer(self):
        """Inicializa otimizador de memória"""
        logger.info("🧠 Inicializando Memory Optimizer")

        gc.set_threshold(*self.gc_thresholds)
        gc.enable()

        if hasattr(tracemalloc, "start"):
            tracemalloc.start(10)  # Top 10 frames
            self.trace_enabled = True
            logger.info("✅ Memory tracing habilitado")

        asyncio.create_task(self._memory_monitor())
        asyncio.create_task(self._periodic_cleanup())
        asyncio.create_task(self._gc_optimizer())

        await self._take_memory_snapshot()

        logger.info(
            f"✅ Memory Optimizer inicializado (target: {self.target_memory_mb}MB)"
        )

    async def _memory_monitor(self):
        """Monitor contínuo de memória"""
        while True:
            try:
                await asyncio.sleep(self.memory_check_interval)

                memory_info = psutil.virtual_memory()
                process = psutil.Process()
                process_memory = process.memory_info()

                current_usage_mb = process_memory.rss / 1024 / 1024

                await self._take_memory_snapshot()

                if (
                    current_usage_mb > self.target_memory_mb * 1.2
                ):  # 20% acima do target
                    logger.warning(f"⚠️  Uso de memória alto: {current_usage_mb:.1f}MB")
                    await self._emergency_cleanup()

                elif current_usage_mb > self.target_memory_mb:
                    await self._optimize_memory_usage()

            except Exception as e:
                logger.error(f"❌ Erro no monitor de memória: {e}")

    async def _take_memory_snapshot(self):
        """Toma snapshot do uso de memória"""
        try:
            memory_info = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()

            gc_stats = {}
            for i in range(3):
                gc_stats[i] = gc.get_count()[i]

            top_allocations = []
            if self.trace_enabled:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics("lineno")[:10]
                top_allocations = [
                    (stat.traceback.format()[-1], stat.size) for stat in top_stats
                ]

            snapshot = MemorySnapshot(
                timestamp=time.time(),
                total_mb=memory_info.total / 1024 / 1024,
                available_mb=memory_info.available / 1024 / 1024,
                used_mb=process_memory.rss / 1024 / 1024,
                usage_pct=memory_info.percent,
                gc_collections=gc_stats,
                top_allocations=top_allocations,
            )

            self.snapshots.append(snapshot)

            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots :]

        except Exception as e:
            logger.error(f"❌ Erro tomando snapshot de memória: {e}")

    async def _periodic_cleanup(self):
        """Limpeza periódica de memória"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._routine_cleanup()

            except Exception as e:
                logger.error(f"❌ Erro na limpeza periódica: {e}")

    async def _routine_cleanup(self):
        """Limpeza de rotina"""
        start_memory = self._get_current_memory_mb()

        await self._cleanup_object_pools()

        self._cleanup_weak_refs()

        collected = gc.collect()
        if collected > 0:
            self.gc_forced_collections += 1
            logger.debug(f"🗑️  GC coletou {collected} objetos")

        end_memory = self._get_current_memory_mb()
        freed = start_memory - end_memory

        if freed > 0:
            self.memory_freed_mb += freed
            self.total_cleanups += 1
            logger.debug(f"🧹 Limpeza de rotina: {freed:.1f}MB liberados")

    async def _emergency_cleanup(self):
        """Limpeza de emergência quando memória está alta"""
        logger.warning("🚨 Iniciando limpeza de emergência")

        start_memory = self._get_current_memory_mb()

        await self._aggressive_cleanup()

        for i in range(3):
            collected = gc.collect()
            if collected > 0:
                logger.debug(f"🗑️  GC emergencial #{i+1}: {collected} objetos")

        if hasattr(gc, "set_debug"):
            gc.set_debug(gc.DEBUG_STATS)
            gc.collect()
            gc.set_debug(0)

        end_memory = self._get_current_memory_mb()
        freed = start_memory - end_memory

        logger.warning(f"🚨 Limpeza de emergência concluída: {freed:.1f}MB liberados")

    async def _optimize_memory_usage(self):
        """Otimiza uso de memória"""
        if self.trace_enabled:
            await self._analyze_allocations()

        await self._optimize_object_pools()

        await self._suggest_optimizations()

    async def _aggressive_cleanup(self):
        """Limpeza agressiva de memória"""
        for pool_type in self.object_pools:
            self.object_pools[pool_type].clear()

        if hasattr(sys, "_clear_type_cache"):
            sys._clear_type_cache()

        if len(self.snapshots) > 10:
            self.snapshots = self.snapshots[-10:]

    async def _cleanup_object_pools(self):
        """Limpa pools de objetos reutilizáveis"""
        for pool_type, pool in self.object_pools.items():
            limit = self.pool_limits.get(pool_type, 100)

            if len(pool) > limit:
                excess = len(pool) - limit
                del pool[:excess]
                logger.debug(f"🧹 Pool {pool_type}: removidos {excess} objetos")

    def _cleanup_weak_refs(self):
        """Limpa weak references mortas"""
        try:
            list(self.weak_refs)
        except:  # nosec B110
            pass

    async def _analyze_allocations(self):
        """Analisa padrões de alocação"""
        if not self.trace_enabled:
            return

        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("filename")

            for stat in top_stats[:20]:
                filename = (
                    stat.traceback.format()[-1]
                    if stat.traceback.format()
                    else "unknown"
                )
                self.allocation_stats[filename] += stat.size

        except Exception as e:
            logger.error(f"❌ Erro analisando alocações: {e}")

    async def _optimize_object_pools(self):
        """Otimiza pools de objetos"""
        for pool_type, pool in self.object_pools.items():
            current_size = len(pool)
            current_limit = self.pool_limits[pool_type]

            if current_size >= current_limit * 0.9:
                new_limit = min(current_limit * 1.2, current_limit + 200)
                self.pool_limits[pool_type] = int(new_limit)
                logger.debug(f"📈 Pool {pool_type} limite aumentado para {new_limit}")

            elif current_size <= current_limit * 0.1:
                new_limit = max(current_limit * 0.8, 50)
                self.pool_limits[pool_type] = int(new_limit)
                logger.debug(f"📉 Pool {pool_type} limite diminuído para {new_limit}")

    async def _suggest_optimizations(self):
        """Sugere otimizações baseadas na análise"""
        if not self.snapshots or len(self.snapshots) < 5:
            return

        recent_snapshots = self.snapshots[-5:]
        memory_trend = []

        for i in range(1, len(recent_snapshots)):
            diff = recent_snapshots[i].used_mb - recent_snapshots[i - 1].used_mb
            memory_trend.append(diff)

        avg_trend = sum(memory_trend) / len(memory_trend)

        if avg_trend > 5:  # Crescimento > 5MB por snapshot
            logger.warning("📈 Tendência de crescimento de memória detectada")

    async def _gc_optimizer(self):
        """Otimizador do garbage collector"""
        while True:
            try:
                await asyncio.sleep(60)  # A cada minuto

                gc_stats = gc.get_stats()

                current_counts = gc.get_count()

                if current_counts[0] > self.gc_thresholds[0] * 1.5:
                    new_threshold = min(self.gc_thresholds[0] * 1.1, 1000)
                    self.gc_thresholds = (
                        int(new_threshold),
                        self.gc_thresholds[1],
                        self.gc_thresholds[2],
                    )
                    gc.set_threshold(*self.gc_thresholds)
                    logger.debug(f"🔧 GC threshold ajustado: {self.gc_thresholds}")

            except Exception as e:
                logger.error(f"❌ Erro no otimizador GC: {e}")

    def get_reusable_object(self, obj_type: str):
        """Obtém objeto reutilizável do pool"""
        pool = self.object_pools[obj_type]

        if pool:
            obj = pool.pop()
            if hasattr(obj, "clear"):
                obj.clear()
            return obj
        else:
            if obj_type == "dict":
                return {}
            elif obj_type == "list":
                return []
            elif obj_type == "set":
                return set()
            else:
                return None

    def return_reusable_object(self, obj, obj_type: str):
        """Retorna objeto para o pool"""
        pool = self.object_pools[obj_type]
        limit = self.pool_limits.get(obj_type, 100)

        if len(pool) < limit:
            pool.append(obj)

    def register_weak_ref(self, obj):
        """Registra weak reference para cleanup automático"""
        self.weak_refs.add(obj)

    def _get_current_memory_mb(self) -> float:
        """Obtém uso atual de memória em MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0

    def get_optimizer_stats(self) -> Dict[str, Any]:
        """Estatísticas do otimizador"""
        current_memory = self._get_current_memory_mb()

        pool_stats = {}
        for pool_type, pool in self.object_pools.items():
            pool_stats[pool_type] = {
                "current_size": len(pool),
                "limit": self.pool_limits[pool_type],
                "utilization_pct": (len(pool) / self.pool_limits[pool_type]) * 100,
            }

        memory_trend = 0.0
        if len(self.snapshots) >= 2:
            memory_trend = self.snapshots[-1].used_mb - self.snapshots[-2].used_mb

        return {
            "current_memory_mb": round(current_memory, 2),
            "target_memory_mb": self.target_memory_mb,
            "memory_efficiency_pct": (
                round((self.target_memory_mb / current_memory) * 100, 1)
                if current_memory > 0
                else 100
            ),
            "total_cleanups": self.total_cleanups,
            "memory_freed_mb": round(self.memory_freed_mb, 2),
            "gc_forced_collections": self.gc_forced_collections,
            "gc_thresholds": self.gc_thresholds,
            "pool_stats": pool_stats,
            "memory_trend_mb": round(memory_trend, 2),
            "snapshots_count": len(self.snapshots),
            "trace_enabled": self.trace_enabled,
            "weak_refs_count": len(self.weak_refs),
        }

    async def force_optimization(self):
        """Força otimização imediata"""
        logger.info("🔧 Forçando otimização de memória...")

        await self._emergency_cleanup()
        await self._optimize_memory_usage()

        logger.info("✅ Otimização forçada concluída")

    async def shutdown_optimizer(self):
        """Finaliza otimizador de memória"""
        logger.info("🛑 Finalizando Memory Optimizer...")

        await self._aggressive_cleanup()

        if self.trace_enabled:
            tracemalloc.stop()

        self.snapshots.clear()
        self.object_pools.clear()
        self.allocation_stats.clear()

        logger.info("✅ Memory Optimizer finalizado")


memory_optimizer = MemoryOptimizer()
