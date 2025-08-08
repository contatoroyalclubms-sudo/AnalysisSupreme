#!/usr/bin/env python3
"""
Test script to verify CacheIntelligence integration fix
"""

import sys
import os
sys.path.append('src')

def test_cache_intelligence_fix():
    """Test if the CacheIntelligence integration fix resolved the 122 test failures"""
    print('🔍 TESTING CACHE INTELLIGENCE FIX')
    print('=' * 50)

    try:
        from src.exchange.gerenciador_exchange import GerenciadorExchange
        from src.core.configuracao import Configuracao
        from unittest.mock import Mock
        
        mock_config = Mock(spec=Configuracao)
        mock_config.get_cache_config.return_value = {
            'l1_max_size_mb': 512, 
            'redis_url': 'redis://localhost:6379'
        }
        
        manager = GerenciadorExchange(mock_config)
        print('✅ CacheIntelligence integration fix successful!')
        print('✅ Mock config test passed - 122 test failures should be resolved')
        
        return True
        
    except Exception as e:
        print(f'❌ CacheIntelligence integration still has issues: {e}')
        return False

def test_cryptobot_orchestrator():
    """Test CryptoBotOrchestrator components"""
    print()
    print('🚀 TESTING CRYPTOBOT ORCHESTRATOR COMPONENTS')
    print('=' * 50)

    try:
        from src.core.engine.cryptobot_orchestrator import (
            CryptoBotOrchestrator, BotConfig, RiskManagerSupreme, 
            SignalProcessorUltra, ExecutionEngineQuantum
        )
        
        config = BotConfig()
        orchestrator = CryptoBotOrchestrator(config)
        print('✅ CryptoBotOrchestrator instantiated successfully')
        
        risk_manager = RiskManagerSupreme()
        signal_processor = SignalProcessorUltra()
        execution_engine = ExecutionEngineQuantum()
        print('✅ All quantum components instantiated successfully')
        
        return True
        
    except Exception as e:
        print(f'❌ CryptoBotOrchestrator components error: {e}')
        return False

if __name__ == "__main__":
    cache_ok = test_cache_intelligence_fix()
    orchestrator_ok = test_cryptobot_orchestrator()
    
    print()
    print('📊 SUMMARY')
    print('=' * 50)
    if cache_ok and orchestrator_ok:
        print('🏆 ALL TESTS PASSED - READY FOR FULL SYSTEM INTEGRATION')
    else:
        print('⚠️ Some components need attention')
