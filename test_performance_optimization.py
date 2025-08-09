#!/usr/bin/env python3
"""
Test script for performance optimizations
"""

import sys
import asyncio
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.configuracao import Configuracao
from src.ia.motor_ia import MotorIA

async def test_motor_ia_performance():
    """Test the optimized MotorIA performance"""
    print("🚀 Testing MotorIA Performance Optimizations")
    print("=" * 50)
    
    config = Configuracao()
    motor = MotorIA(config._config)
    await motor.inicializar()
    
    dados_mercado = {
        'ohlcv': [[50000 + i, 50100 + i, 49900 + i, 50050 + i, 1000] for i in range(100)],
        'precos': [50000 + i for i in range(100)],
        'volumes': [1000 + i for i in range(100)],
        'preco_atual': 50050
    }
    
    symbols = ['BTC', 'ETH', 'ADA']
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol} analysis...")
        
        start = time.time()
        result1 = await motor.analisar_mercado(dados_mercado, symbol)
        end = time.time()
        time1 = (end - start) * 1000
        
        start = time.time()
        result2 = await motor.analisar_mercado(dados_mercado, symbol)
        end = time.time()
        time2 = (end - start) * 1000
        
        print(f"  First run (cache miss): {time1:.2f}ms")
        print(f"  Second run (cache hit): {time2:.2f}ms")
        print(f"  Performance improvement: {((time1 - time2) / time1 * 100):.1f}%")
        print(f"  Target met (<100ms): {'✅' if time2 < 100 else '❌'}")
        print(f"  Cached result: {result2.get('cached', False)}")

if __name__ == "__main__":
    asyncio.run(test_motor_ia_performance())
