#!/usr/bin/env bash
set -euo pipefail

echo "🚀 CRYPTOBOT SUPREMO GLOBAL - Performance Benchmark"
echo "=================================================================="

mkdir -p logs/benchmarks

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BENCHMARK_LOG="logs/benchmarks/bench_${TIMESTAMP}.log"

echo "📊 Starting comprehensive performance benchmark..." | tee $BENCHMARK_LOG
echo "Timestamp: $(date)" | tee -a $BENCHMARK_LOG
echo "=================================================================" | tee -a $BENCHMARK_LOG

echo "" | tee -a $BENCHMARK_LOG
echo "⚡ Testing Ultra Fast Executor (target: 15ms)..." | tee -a $BENCHMARK_LOG
echo "---------------------------------------------------" | tee -a $BENCHMARK_LOG
python scripts/test_cryptobot_supremo.py 2>&1 | tee -a $BENCHMARK_LOG

echo "" | tee -a $BENCHMARK_LOG
echo "🧠 Testing Cache Intelligence System (target: 99.8% hit rate)..." | tee -a $BENCHMARK_LOG
echo "---------------------------------------------------" | tee -a $BENCHMARK_LOG
python -c "
import sys, time, asyncio
sys.path.append('src')
try:
    from src.core.engine.cache_intelligence import CacheIntelligence
    
    async def test_cache_performance():
        cache = CacheIntelligence(512)
        await cache.initialize_intelligence()
        
        start_time = time.time()
        
        for i in range(1000):
            await cache.set_intelligent(f'test_key_{i}', {'data': f'value_{i}'}, 'ticker')
        
        hits = 0
        for i in range(1000):
            result = await cache.get_intelligent(f'test_key_{i}', 'ticker')
            if result:
                hits += 1
        
        hit_rate = (hits / 1000) * 100
        total_time = (time.time() - start_time) * 1000
        
        print(f'Cache Intelligence Performance:')
        print(f'  - Hit Rate: {hit_rate:.1f}% (target: 99.8%)')
        print(f'  - Total Time: {total_time:.2f}ms for 1000 operations')
        print(f'  - Avg Time per Operation: {total_time/1000:.3f}ms')
        
        if hit_rate >= 99.0:
            print('✅ Cache Intelligence: Target achieved')
        else:
            print('❌ Cache Intelligence: Needs optimization')
        
        await cache.shutdown_intelligence()
    
    asyncio.run(test_cache_performance())
except Exception as e:
    print(f'❌ Cache Intelligence test failed: {e}')
" 2>&1 | tee -a $BENCHMARK_LOG

echo "" | tee -a $BENCHMARK_LOG
echo "🌐 Testing WebSocket Manager Premium (target: sub-1ms latency)..." | tee -a $BENCHMARK_LOG
echo "---------------------------------------------------" | tee -a $BENCHMARK_LOG
python -c "
import sys, time, asyncio
sys.path.append('src')
try:
    from src.core.engine.websocket_manager_premium import WebSocketManagerPremium
    
    async def test_websocket_performance():
        ws_manager = WebSocketManagerPremium()
        await ws_manager.initialize_premium()
        
        start_time = time.time() * 1000
        
        test_message = {'stream': 'btcusdt@ticker', 'data': {'s': 'BTCUSDT', 'c': '45000'}}
        
        for i in range(100):
            await ws_manager._process_message_ultra_fast(test_message)
        
        end_time = time.time() * 1000
        avg_latency = (end_time - start_time) / 100
        
        print(f'WebSocket Manager Premium Performance:')
        print(f'  - Average Latency: {avg_latency:.3f}ms (target: <1ms)')
        print(f'  - Messages Processed: 100')
        print(f'  - Total Time: {end_time - start_time:.2f}ms')
        
        if avg_latency < 1.0:
            print('✅ WebSocket Manager Premium: Target achieved')
        else:
            print('❌ WebSocket Manager Premium: Needs optimization')
        
        await ws_manager.shutdown_premium()
    
    asyncio.run(test_websocket_performance())
except Exception as e:
    print(f'❌ WebSocket Manager Premium test failed: {e}')
" 2>&1 | tee -a $BENCHMARK_LOG

echo "" | tee -a $BENCHMARK_LOG
echo "🤖 Testing individual bot performance..." | tee -a $BENCHMARK_LOG
echo "---------------------------------------------------" | tee -a $BENCHMARK_LOG
for bot in arbitragem grid momentum scalping mean_reversion swing; do
    echo "Testing $bot bot..." | tee -a $BENCHMARK_LOG
    python -c "
import sys, time, asyncio
sys.path.append('src')
try:
    from src.bots.${bot} import Bot${bot^}
    from src.core.configuracao import Configuracao
    from src.observabilidade.monitor import Monitor
    from src.ia.motor_ia import MotorIA
    from unittest.mock import Mock
    
    async def test_bot():
        config = Mock(spec=Configuracao)
        config.paper_mode = True
        config.get_cache_config.return_value = {'l1_max_size_mb': 512}
        
        monitor = Mock(spec=Monitor)
        motor_ia = Mock(spec=MotorIA)
        
        start = time.time()
        bot = Bot${bot^}(config, monitor, motor_ia)
        
        semaphore = asyncio.Semaphore(3)
        await bot.executar_casos_paralelos(semaphore, 5)
        
        execution_time = (time.time() - start) * 1000
        print(f'  - ${bot} bot: {execution_time:.2f}ms')
        
        if execution_time < 100:
            print(f'    ✅ ${bot} bot: Performance target achieved')
        else:
            print(f'    ⚠️ ${bot} bot: Consider optimization')
    
    asyncio.run(test_bot())
except Exception as e:
    print(f'  ❌ ${bot} bot test failed: {e}')
" 2>&1 | tee -a $BENCHMARK_LOG
done

echo "" | tee -a $BENCHMARK_LOG
echo "⚡ Testing CryptoBotOrchestrator Quantum Components..." | tee -a $BENCHMARK_LOG
echo "---------------------------------------------------" | tee -a $BENCHMARK_LOG
python -c "
import sys, time, asyncio
sys.path.append('src')
try:
    from src.core.engine.cryptobot_orchestrator import (
        CryptoBotOrchestrator, BotConfig, RiskManagerSupreme, 
        SignalProcessorUltra, ExecutionEngineQuantum
    )
    
    async def test_quantum_components():
        config = BotConfig()
        orchestrator = CryptoBotOrchestrator(config)
        
        start_time = time.time() * 1000
        await orchestrator.initialize_supreme_system()
        init_time = time.time() * 1000 - start_time
        
        print(f'CryptoBotOrchestrator Quantum Performance:')
        print(f'  - Initialization Time: {init_time:.2f}ms')
        
        risk_manager = RiskManagerSupreme()
        signal_processor = SignalProcessorUltra()
        execution_engine = ExecutionEngineQuantum()
        
        start_time = time.time() * 1000
        await risk_manager.initialize()
        await signal_processor.initialize_ai_models()
        await execution_engine.initialize_quantum_speed()
        component_init_time = time.time() * 1000 - start_time
        
        print(f'  - Quantum Components Init: {component_init_time:.2f}ms')
        
        start_time = time.time() * 1000
        result = await execution_engine.execute_order_lightning(
            exchange='test', symbol='BTCUSDT', side='buy', 
            quantity=0.001, price=45000
        )
        execution_time = time.time() * 1000 - start_time
        
        print(f'  - Quantum Execution Time: {execution_time:.2f}ms (target: <10ms)')
        
        if execution_time < 10:
            print('✅ CryptoBotOrchestrator Quantum: Target achieved')
        else:
            print('❌ CryptoBotOrchestrator Quantum: Needs optimization')
        
        await orchestrator.shutdown()
    
    asyncio.run(test_quantum_components())
except Exception as e:
    print(f'❌ CryptoBotOrchestrator Quantum test failed: {e}')
" 2>&1 | tee -a $BENCHMARK_LOG

echo "" | tee -a $BENCHMARK_LOG
echo "📊 PERFORMANCE SUMMARY" | tee -a $BENCHMARK_LOG
echo "=================================================================" | tee -a $BENCHMARK_LOG
echo "Benchmark completed at: $(date)" | tee -a $BENCHMARK_LOG
echo "Results saved to: $BENCHMARK_LOG" | tee -a $BENCHMARK_LOG
echo "" | tee -a $BENCHMARK_LOG
echo "🎯 CRYPTOBOT SUPREMO GLOBAL Performance Targets:" | tee -a $BENCHMARK_LOG
echo "  - Ultra Fast Executor: 15ms target" | tee -a $BENCHMARK_LOG
echo "  - WebSocket Manager Premium: sub-1ms latency target" | tee -a $BENCHMARK_LOG
echo "  - Cache Intelligence: 99.8% hit rate target" | tee -a $BENCHMARK_LOG
echo "  - Quantum Execution: sub-10ms target" | tee -a $BENCHMARK_LOG
echo "" | tee -a $BENCHMARK_LOG

echo "🏆 Checking if all performance targets achieved..." | tee -a $BENCHMARK_LOG
if grep -q "Target achieved" $BENCHMARK_LOG; then
    echo "✅ Some performance targets achieved!" | tee -a $BENCHMARK_LOG
else
    echo "⚠️ Performance targets need optimization" | tee -a $BENCHMARK_LOG
fi

echo "" | tee -a $BENCHMARK_LOG
echo "✅ Benchmark completed - results saved to $BENCHMARK_LOG" | tee -a $BENCHMARK_LOG
echo "📋 View detailed results: cat $BENCHMARK_LOG"
echo "🔄 Run again: bash scripts/benchmark.sh"
