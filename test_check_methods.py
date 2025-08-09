#!/usr/bin/env python3
"""
Test script to check if all required methods are implemented
"""
import sys
sys.path.insert(0, '.')

def check_sentiment_analyzer():
    try:
        from src.ia.sentiment_analyzer import SentimentAnalyzer
        sa = SentimentAnalyzer()
        
        methods = ['_obter_noticias', '_obter_tweets', '_obter_posts_reddit', 
                  'obter_noticias', 'extrair_features', 'analisar_sentimento']
        
        missing = []
        for method in methods:
            if not hasattr(sa, method):
                missing.append(method)
        
        print(f"SentimentAnalyzer - Missing methods: {missing}")
        return len(missing) == 0
        
    except Exception as e:
        print(f"SentimentAnalyzer - Error: {e}")
        return False

def check_aprendizado_continuo():
    try:
        from src.ia.aprendizado_continuo import AprendizadoContinuo
        ac = AprendizadoContinuo()
        
        methods = ['_calcular_reward', '_atualizar_politica', 'adicionar_trade', 
                  'calcular_reward', 'treinar_modelo']
        
        missing = []
        for method in methods:
            if not hasattr(ac, method):
                missing.append(method)
        
        print(f"AprendizadoContinuo - Missing methods: {missing}")
        return len(missing) == 0
        
    except Exception as e:
        print(f"AprendizadoContinuo - Error: {e}")
        return False

def check_gerador_sinais():
    try:
        from src.ia.gerador_sinais import GeradorSinais
        gs = GeradorSinais()
        
        methods = ['_calcular_indicadores_tecnicos', '_combinar_sinais', 'analisar_mercado',
                  'calcular_rsi', 'calcular_macd', 'calcular_bandas_bollinger', 'gerar_sinal']
        
        missing = []
        for method in methods:
            if not hasattr(gs, method):
                missing.append(method)
        
        print(f"GeradorSinais - Missing methods: {missing}")
        return len(missing) == 0
        
    except Exception as e:
        print(f"GeradorSinais - Error: {e}")
        return False

def check_autotuner():
    try:
        from src.optimization.autotuner import AutoTuner
        at = AutoTuner()
        
        methods = ['otimizar_parametros', '_avaliar_fitness', '_algoritmo_genetico']
        
        missing = []
        for method in methods:
            if not hasattr(at, method):
                missing.append(method)
        
        print(f"AutoTuner - Missing methods: {missing}")
        return len(missing) == 0
        
    except Exception as e:
        print(f"AutoTuner - Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking IA class implementations...")
    
    results = {
        'SentimentAnalyzer': check_sentiment_analyzer(),
        'AprendizadoContinuo': check_aprendizado_continuo(), 
        'GeradorSinais': check_gerador_sinais(),
        'AutoTuner': check_autotuner()
    }
    
    print("\n📊 Results:")
    for class_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {class_name}: {'OK' if status else 'MISSING METHODS'}")
    
    all_good = all(results.values())
    print(f"\n🎯 Overall Status: {'✅ ALL GOOD' if all_good else '❌ NEEDS FIXES'}")
