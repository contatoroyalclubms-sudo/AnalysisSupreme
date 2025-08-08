#!/usr/bin/env python3
"""
Script para testar imports das otimizações de performance
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_performance_imports():
    """Testa se todos os módulos de performance podem ser importados"""
    try:
        from src.exchange.websocket_pool import WebSocketPool
        print('✅ WebSocket Pool imported successfully')
        
        from src.cache.redis_cache import RedisCache
        print('✅ Redis Cache imported successfully')
        
        from src.utils.circuit_breaker import CircuitBreaker
        print('✅ Circuit Breaker imported successfully')
        
        from src.performance.benchmark import PerformanceBenchmark
        print('✅ Performance Benchmark imported successfully')
        
        pool = WebSocketPool(max_connections_per_exchange=5)
        print('✅ WebSocket Pool instantiated')
        
        cache = RedisCache({})
        print('✅ Redis Cache instantiated')
        
        breaker = CircuitBreaker()
        print('✅ Circuit Breaker instantiated')
        
        print('🚀 All performance optimizations ready!')
        return True
        
    except Exception as e:
        print(f'❌ Error importing performance modules: {e}')
        return False

if __name__ == "__main__":
    success = test_performance_imports()
    sys.exit(0 if success else 1)
