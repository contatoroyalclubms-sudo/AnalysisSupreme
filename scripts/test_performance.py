#!/usr/bin/env python3
"""
Script para testar performance do sistema AnalysisSupreme
"""

import asyncio
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.configuracao import Configuracao
from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.core.gerenciador_bots import GerenciadorBots
from src.observabilidade.monitor import Monitor
from src.ia.motor_ia import MotorIA
from src.performance.benchmark import PerformanceBenchmark


async def main():
    parser = argparse.ArgumentParser(description="Teste de performance AnalysisSupreme")
    parser.add_argument("--test", choices=["latency", "throughput", "bots", "full"], default="full", help="Tipo de teste")
    parser.add_argument("--duration", type=int, default=60, help="Duração do teste em segundos")
    parser.add_argument("--iterations", type=int, default=100, help="Número de iterações para teste de latência")

    args = parser.parse_args()

    print("🚀 INICIANDO TESTES DE PERFORMANCE - ANALYSISSUPREME")
    print("=" * 60)

    config = Configuracao()
    exchange_manager = GerenciadorExchange(config)
    monitor = Monitor(config)
    motor_ia = MotorIA(config)
    bot_manager = GerenciadorBots(config, monitor, motor_ia)

    await exchange_manager.inicializar()
    await monitor.inicializar()
    await motor_ia.inicializar()
    await bot_manager.inicializar()

    benchmark = PerformanceBenchmark(exchange_manager, bot_manager)

    try:
        if args.test == "latency":
            print(f"📊 Executando teste de latência ({args.iterations} iterações)...")
            results = await benchmark.run_latency_benchmark(args.iterations)
            print_latency_results(results)

        elif args.test == "throughput":
            print(f"⚡ Executando teste de throughput ({args.duration}s)...")
            results = await benchmark.run_throughput_benchmark(args.duration)
            print_throughput_results(results)

        elif args.test == "full":
            print("🎯 Executando relatório completo de performance...")
            results = await benchmark.generate_performance_report()
            print_full_results(results)

    finally:
        await bot_manager.finalizar()
        await motor_ia.finalizar()
        await monitor.finalizar()
        await exchange_manager.finalizar()


def print_latency_results(results):
    """Imprime resultados de latência"""
    print("\n📊 RESULTADOS DE LATÊNCIA:")
    print("-" * 40)

    for operation in ["ticker", "orderbook", "ohlcv"]:
        if f"{operation}_stats" in results:
            stats = results[f"{operation}_stats"]
            print(f"\n{operation.upper()}:")
            print(f"  Média: {stats['mean']:.2f}ms")
            print(f"  Mediana: {stats['median']:.2f}ms")
            print(f"  P95: {stats['p95']:.2f}ms")
            print(f"  P99: {stats['p99']:.2f}ms")
            print(f"  Min/Max: {stats['min']:.2f}ms / {stats['max']:.2f}ms")


def print_throughput_results(results):
    """Imprime resultados de throughput"""
    print("\n⚡ RESULTADOS DE THROUGHPUT:")
    print("-" * 40)
    print(f"Duração: {results['duration_seconds']:.1f}s")
    print(f"Total de operações: {results['total_operations']}")

    for operation, ops_per_sec in results["operations_per_second"].items():
        print(f"{operation}: {ops_per_sec:.1f} ops/s")


def print_full_results(results):
    """Imprime resultados completos"""
    print("\n🎯 RELATÓRIO COMPLETO DE PERFORMANCE:")
    print("-" * 50)

    targets = results["targets_met"]
    print("\nTARGETS ATINGIDOS:")
    for target, met in targets.items():
        status = "✅" if met else "❌"
        print(f"  {status} {target}")

    if "latency_benchmark" in results:
        ticker_stats = results["latency_benchmark"].get("ticker_stats", {})
        print(f"\nLatência média ticker: {ticker_stats.get('mean', 0):.2f}ms")

    if "throughput_benchmark" in results:
        throughput = results["throughput_benchmark"]["operations_per_second"].get("ticker", 0)
        print(f"Throughput ticker: {throughput:.1f} ops/s")

    cache_stats = results["current_stats"]["exchange"]["cache"]
    print(f"Cache hit rate: {cache_stats['hit_rate']}")


if __name__ == "__main__":
    asyncio.run(main())
