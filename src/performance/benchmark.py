"""
Sistema de benchmark e monitoramento de performance
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Sistema de benchmark para medir performance do sistema"""

    def __init__(self, exchange_manager: Any, bot_manager: Any):
        self.exchange_manager = exchange_manager
        self.bot_manager = bot_manager
        self.benchmark_results: Dict[str, Any] = {}
        self.ticker_latencies: List[float] = []
        self.orderbook_latencies: List[float] = []
        self.ohlcv_latencies: List[float] = []
        self.metrics: Dict[str, float] = {}
        self.timestamps: List[float] = []

    async def run_latency_benchmark(self, iterations: int = 100) -> Dict[str, Any]:
        """Executa benchmark de latência para operações de exchange"""
        logger.info(f"Iniciando benchmark de latência com {iterations} iterações")

        results: Dict[str, Any] = {
            "ticker_latencies": [],
            "orderbook_latencies": [],
            "ohlcv_latencies": [],
            "timestamp": datetime.now().isoformat(),
        }

        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

        for i in range(iterations):
            start_time = time.time() * 1000

            tasks = [self.exchange_manager.get_ticker(symbol) for symbol in symbols]
            await asyncio.gather(*tasks)

            end_time = time.time() * 1000
            latency = end_time - start_time
            results["ticker_latencies"].append(latency)

            if i % 20 == 0:
                logger.info(
                    f"Benchmark ticker: {i}/{iterations} - Latência: {latency:.2f}ms"
                )

        for i in range(iterations // 2):
            start_time = time.time() * 1000

            tasks = [
                self.exchange_manager.get_orderbook(symbol, 10) for symbol in symbols
            ]
            await asyncio.gather(*tasks)

            end_time = time.time() * 1000
            latency = end_time - start_time
            results["orderbook_latencies"].append(latency)

        for i in range(iterations // 4):
            start_time = time.time() * 1000

            tasks = [
                self.exchange_manager.get_ohlcv(symbol, "1m", 50) for symbol in symbols
            ]
            await asyncio.gather(*tasks)

            end_time = time.time() * 1000
            latency = end_time - start_time
            results["ohlcv_latencies"].append(latency)

        stats = self._calculate_latency_stats(results)
        results.update(stats)

        logger.info("Benchmark de latência concluído")
        return results

    def _calculate_latency_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estatísticas de latência"""
        stats = {}

        for operation in ["ticker", "orderbook", "ohlcv"]:
            latencies = results[f"{operation}_latencies"]

            if latencies:
                stats[f"{operation}_stats"] = {
                    "mean": statistics.mean(latencies),
                    "median": statistics.median(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                    "p95": self._percentile(latencies, 95),
                    "p99": self._percentile(latencies, 99),
                    "std_dev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                }

        return stats

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcula percentil dos dados"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)

        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    async def run_throughput_benchmark(
        self, duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """Executa benchmark de throughput"""
        logger.info(f"Iniciando benchmark de throughput por {duration_seconds}s")

        start_time = time.time()
        end_time = start_time + duration_seconds

        operation_counts = {
            "ticker_requests": 0,
            "orderbook_requests": 0,
            "cache_hits": 0,
            "websocket_messages": 0,
        }

        initial_stats = self.exchange_manager.get_performance_stats()

        tasks = []
        tasks.append(self._continuous_ticker_requests(end_time, operation_counts))
        tasks.append(self._continuous_orderbook_requests(end_time, operation_counts))

        await asyncio.gather(*tasks)

        final_stats = self.exchange_manager.get_performance_stats()

        actual_duration = time.time() - start_time

        results = {
            "duration_seconds": actual_duration,
            "operations_per_second": {
                "ticker": operation_counts["ticker_requests"] / actual_duration,
                "orderbook": operation_counts["orderbook_requests"] / actual_duration,
            },
            "total_operations": sum(operation_counts.values()),
            "cache_performance": {
                "initial_hits": initial_stats["cache"]["hits"],
                "final_hits": final_stats["cache"]["hits"],
                "hits_during_test": final_stats["cache"]["hits"]
                - initial_stats["cache"]["hits"],
            },
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Benchmark de throughput concluído: {results['total_operations']} operações"
        )
        return results

    async def _continuous_ticker_requests(
        self, end_time: float, counters: Dict[str, int]
    ):
        """Executa requisições contínuas de ticker"""
        symbols = ["BTC/USDT", "ETH/USDT"]

        while time.time() < end_time:
            try:
                tasks = [self.exchange_manager.get_ticker(symbol) for symbol in symbols]
                await asyncio.gather(*tasks)
                counters["ticker_requests"] += len(symbols)

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Erro em benchmark ticker: {e}")

    async def _continuous_orderbook_requests(
        self, end_time: float, counters: Dict[str, int]
    ):
        """Executa requisições contínuas de orderbook"""
        symbols = ["BTC/USDT"]

        while time.time() < end_time:
            try:
                tasks = [
                    self.exchange_manager.get_orderbook(symbol, 5) for symbol in symbols
                ]
                await asyncio.gather(*tasks)
                counters["orderbook_requests"] += len(symbols)

                await asyncio.sleep(0.2)

            except Exception as e:
                logger.error(f"Erro em benchmark orderbook: {e}")

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Gera relatório completo de performance"""
        logger.info("Gerando relatório completo de performance")

        latency_results = await self.run_latency_benchmark(50)
        throughput_results = await self.run_throughput_benchmark(30)

        exchange_stats = self.exchange_manager.get_performance_stats()
        bot_stats = self.bot_manager.get_metricas_consolidadas()

        report = {
            "timestamp": datetime.now().isoformat(),
            "latency_benchmark": latency_results,
            "throughput_benchmark": throughput_results,
            "current_stats": {"exchange": exchange_stats, "bots": bot_stats},
            "performance_targets": {
                "general_latency_ms": 120,
                "arbitrage_latency_ms": 50,
                "scalping_latency_ms": 30,
                "min_throughput_ops_per_sec": 10,
            },
        }

        report["targets_met"] = self._check_performance_targets(report)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"logs/performance_report_{timestamp}.json"

        import os

        os.makedirs("logs", exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)

        logger.info(f"Relatório de performance salvo: {report_path}")
        return report

    def _check_performance_targets(self, report: Dict[str, Any]) -> Dict[str, bool]:
        """Verifica se targets de performance foram atingidos"""
        targets = report["performance_targets"]
        latency_stats = report["latency_benchmark"]

        return {
            "general_latency": latency_stats.get("ticker_stats", {}).get("mean", 999)
            < targets["general_latency_ms"],
            "throughput": report["throughput_benchmark"]["operations_per_second"].get(
                "ticker", 0
            )
            > targets["min_throughput_ops_per_sec"],
            "cache_hit_rate": float(
                report["current_stats"]["exchange"]["cache"]["hit_rate"].replace(
                    "%", ""
                )
            )
            > 50.0,
        }
