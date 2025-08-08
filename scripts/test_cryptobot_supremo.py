#!/usr/bin/env python3
"""
Script para testar CRYPTOBOT SUPREMO GLOBAL
Testa engine ultra-rápido (15ms), WebSocket premium, cache neural e Sinfonia Tecnológica
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_cryptobot_supremo():
    """Testa todos os componentes do CRYPTOBOT SUPREMO GLOBAL"""
    print("🚀 TESTANDO CRYPTOBOT SUPREMO GLOBAL")
    print("=" * 60)
    
    print("⚡ Testando Ultra Fast Executor (target: 15ms)...")
    try:
        from src.core.engine.ultra_fast_executor import UltraFastExecutor, ExecutionTask
        
        executor = UltraFastExecutor()
        await executor.initialize()
        
        start_time = time.time() * 1000
        task = ExecutionTask(
            task_id="test_ultra",
            bot_name="arbitragem",
            action="test",
            params={},
            priority=9
        )
        
        result = await executor.execute_ultra_fast(task)
        execution_time = time.time() * 1000 - start_time
        
        print(f"✅ Ultra Fast Executor: {execution_time:.2f}ms (target: 15ms)")
        
        await executor.shutdown()
        
    except Exception as e:
        print(f"❌ Ultra Fast Executor error: {e}")
    
    print("🌐 Testando WebSocket Manager Premium (target: sub-1ms)...")
    try:
        from src.core.engine.websocket_manager_premium import WebSocketManagerPremium
        
        ws_manager = WebSocketManagerPremium()
        await ws_manager.initialize_premium()
        
        stats = ws_manager.get_premium_stats()
        print(f"✅ WebSocket Manager Premium: {stats['total_connections']} conexões")
        
        await ws_manager.shutdown_premium()
        
    except Exception as e:
        print(f"❌ WebSocket Manager Premium error: {e}")
    
    print("🧠 Testando Cache Intelligence (target: 99.8% hit rate)...")
    try:
        from src.core.engine.cache_intelligence import CacheIntelligence
        
        cache = CacheIntelligence()
        await cache.initialize()
        
        await cache.set("test_key", {"data": "test"})
        result = await cache.get("test_key")
        
        stats = cache.get_stats()
        print(f"✅ Cache Intelligence: {stats['overall_hit_rate']} hit rate")
        
        await cache.shutdown()
        
    except Exception as e:
        print(f"❌ Cache Intelligence error: {e}")
    
    print("🎼 Testando Sinfonia Tecnológica Suprema...")
    try:
        from src.core.engine.sinfonia_suprema import SinfoniaSuprema
        
        sinfonia = SinfoniaSuprema()
        await sinfonia.initialize_sinfonia()
        
        async def test_func():
            return {"result": "success"}
        
        result = await sinfonia.execute_movimento("arbitragem", test_func)
        
        symphony_report = sinfonia.get_performance_symphony()
        print(f"✅ Sinfonia Tecnológica: {len(symphony_report['componentes'])} componentes ativos")
        
        await sinfonia.finale_graceful_shutdown()
        
    except Exception as e:
        print(f"❌ Sinfonia Tecnológica error: {e}")
    
    print("\n🎯 CRYPTOBOT SUPREMO GLOBAL - Testes concluídos!")

if __name__ == "__main__":
    asyncio.run(test_cryptobot_supremo())
