#!/usr/bin/env python3
"""
Script para monitoramento contínuo de performance
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.configuracao import Configuracao
from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.core.gerenciador_bots import GerenciadorBots
from src.observabilidade.monitor import Monitor
from src.ia.motor_ia import MotorIA

async def main():
    print("👁️  INICIANDO MONITORAMENTO DE PERFORMANCE")
    print("=" * 50)
    
    config = Configuracao()
    exchange_manager = GerenciadorExchange(config)
    monitor = Monitor(config)
    motor_ia = MotorIA(config)
    bot_manager = GerenciadorBots(config, monitor, motor_ia)
    
    await exchange_manager.inicializar()
    await monitor.inicializar()
    await motor_ia.inicializar()
    await bot_manager.inicializar()
    
    try:
        print("🔄 Monitoramento ativo - Pressione Ctrl+C para parar")
        
        while True:
            stats = exchange_manager.get_performance_stats()
            
            print(f"\n⏰ {time.strftime('%H:%M:%S')}")
            print(f"📊 Requests: {stats['requests']['total_requests']}")
            print(f"💾 Cache hits: {stats['cache']['hits']}")
            print(f"📈 Hit rate: {stats['cache']['hit_rate']}")
            print(f"🌐 WebSocket msgs: {stats['requests']['websocket_messages']}")
            
            circuit_states = stats['circuit_breakers']
            for exchange, state in circuit_states.items():
                status_emoji = "🟢" if state['state'] == 'closed' else "🔴" if state['state'] == 'open' else "🟡"
                print(f"{status_emoji} {exchange}: {state['state']}")
            
            await asyncio.sleep(5)
    
    except KeyboardInterrupt:
        print("\n🛑 Parando monitoramento...")
    
    finally:
        await bot_manager.finalizar()
        await motor_ia.finalizar()
        await monitor.finalizar()
        await exchange_manager.finalizar()

if __name__ == "__main__":
    asyncio.run(main())
