"""
Testes abrangentes para componentes de IA
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from datetime import datetime

from src.ia.motor_ia import MotorIA, GeradorSinais, AutoTuner, SentimentAnalyzer, AprendizadoContinuo
from src.core.configuracao import Configuracao
from src.models.trade import Trade


class TestGeradorSinaisAbrangente:
    """Testes abrangentes para gerador de sinais"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_ia_config.return_value = Mock(
            modelo_path="models/",
            indicadores_ativos=True,
            ml_habilitado=True
        )
        return config
    
    def test_inicializacao_gerador_sinais(self, mock_config):
        """Testa inicialização do gerador de sinais"""
        gerador = GeradorSinais()
        
        assert hasattr(gerador, 'indicadores')
        assert hasattr(gerador, 'pesos')
    
    def test_calcular_indicadores_basicos(self, mock_config):
        """Testa cálculo de indicadores básicos"""
        gerador = GeradorSinais()
        
        precos = [50000, 50100, 49900, 50200, 49800, 50300, 49700, 50400]
        volumes = [100, 120, 80, 150, 90, 130, 70, 140]
        
        indicadores = gerador.calcular_indicadores_basicos(precos, volumes)
        
        assert isinstance(indicadores, dict)
        assert "sma" in indicadores
        assert "rsi" in indicadores
        assert "volume_avg" in indicadores
    
    def test_calcular_sma(self, mock_config):
        """Testa cálculo de SMA"""
        gerador = GeradorSinais()
        
        precos = [50000, 50100, 49900, 50200, 49800]
        sma = gerador._calcular_sma(precos, 3)
        
        assert isinstance(sma, float)
        assert sma > 0
    
    def test_calcular_ema(self, mock_config):
        """Testa cálculo de EMA"""
        gerador = GeradorSinais()
        
        precos = [50000, 50100, 49900, 50200, 49800]
        ema = gerador._calcular_ema(precos, 3)
        
        assert isinstance(ema, float)
        assert ema > 0
    
    def test_calcular_rsi(self, mock_config):
        """Testa cálculo de RSI"""
        gerador = GeradorSinais()
        
        precos = [50000, 50100, 49900, 50200, 49800, 50300, 49700, 50400]
        rsi = gerador._calcular_rsi(precos, 7)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
    
    def test_calcular_macd(self, mock_config):
        """Testa cálculo de MACD"""
        gerador = GeradorSinais()
        
        precos = [50000 + i*10 for i in range(30)]
        macd, signal = gerador._calcular_macd(precos)
        
        assert isinstance(macd, float)
        assert isinstance(signal, float)
    
    def test_analisar_mercado_completo(self, mock_config):
        """Testa análise completa do mercado"""
        gerador = GeradorSinais()
        
        dados_market = {
            "symbol": "BTC/USDT",
            "ohlcv": [[i, 50000+i*10, 50100+i*10, 49900+i*10, 50000+i*10, 100] for i in range(20)],
            "orderbook": {"bids": [[49999, 1.0]], "asks": [[50001, 1.0]]},
            "ticker": {"last": 50000, "volume": 1000}
        }
        
        sinal = gerador.analisar_mercado(dados_market)
        
        assert sinal is not None
        assert hasattr(sinal, 'acao')
        assert hasattr(sinal, 'confidence')
        assert sinal.acao in ['comprar', 'vender', 'aguardar']
        assert 0 <= sinal.confidence <= 1


class TestAutoTunerAbrangente:
    """Testes abrangentes para auto tuner"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_ia_config.return_value = Mock(
            otimizacao_ativa=True,
            algoritmo_genetico=True,
            otimizacao_bayesiana=True
        )
        return config
    
    def test_inicializacao_auto_tuner(self, mock_config):
        """Testa inicialização do auto tuner"""
        tuner = AutoTuner()
        
        assert hasattr(tuner, 'historico_otimizacoes')
    
    def test_otimizar_parametros_arbitragem(self, mock_config):
        """Testa otimização de parâmetros para arbitragem"""
        tuner = AutoTuner()
        
        estrategia = "arbitragem"
        historico = [
            Trade(id="1", bot="arbitragem", symbol="BTC/USDT", side="buy", 
                  amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=100),
            Trade(id="2", bot="arbitragem", symbol="BTC/USDT", side="sell", 
                  amount=0.01, price=50100, timestamp=datetime.now(), caso_uso=1, pnl=50)
        ]
        
        parametros_otimizados = tuner.otimizar_parametros(estrategia, historico)
        
        assert isinstance(parametros_otimizados, dict)
        assert "spread_minimo" in parametros_otimizados
        assert "timeout_execucao" in parametros_otimizados
    
    def test_otimizar_parametros_grid(self, mock_config):
        """Testa otimização de parâmetros para grid"""
        tuner = AutoTuner()
        
        estrategia = "grid"
        historico = [
            Trade(id="1", bot="grid", symbol="BTC/USDT", side="buy", 
                  amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=75),
            Trade(id="2", bot="grid", symbol="BTC/USDT", side="sell", 
                  amount=0.01, price=50050, timestamp=datetime.now(), caso_uso=1, pnl=25)
        ]
        
        parametros_otimizados = tuner.otimizar_parametros(estrategia, historico)
        
        assert isinstance(parametros_otimizados, dict)
        assert "grid_levels" in parametros_otimizados
        assert "range_percent" in parametros_otimizados
    
    def test_calcular_fitness(self, mock_config):
        """Testa cálculo de fitness"""
        tuner = AutoTuner()
        
        trades = [
            Trade(id="1", bot="momentum", symbol="BTC/USDT", side="buy", 
                  amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=100),
            Trade(id="2", bot="momentum", symbol="BTC/USDT", side="sell", 
                  amount=0.01, price=49900, timestamp=datetime.now(), caso_uso=1, pnl=-50)
        ]
        
        fitness = tuner._calcular_fitness(trades)
        
        assert isinstance(fitness, float)
        assert fitness >= 0
    
    def test_gerar_parametros_aleatorios(self, mock_config):
        """Testa geração de parâmetros aleatórios"""
        tuner = AutoTuner()
        
        parametros = tuner._gerar_parametros_aleatorios("scalping")
        
        assert isinstance(parametros, dict)
        assert len(parametros) > 0
        
        for key, value in parametros.items():
            assert isinstance(value, (int, float))


class TestSentimentAnalyzerAbrangente:
    """Testes abrangentes para analisador de sentimento"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_ia_config.return_value = Mock(
            sentiment_ativo=True,
            fontes_sentiment=["twitter", "reddit", "news"]
        )
        return config
    
    def test_inicializacao_sentiment_analyzer(self, mock_config):
        """Testa inicialização do analisador de sentimento"""
        analyzer = SentimentAnalyzer()
        
        assert hasattr(analyzer, 'cache_sentiment')
    
    @patch('requests.get')
    def test_analisar_sentimento_mock(self, mock_get, mock_config):
        """Testa análise de sentimento com mock"""
        mock_get.return_value.json.return_value = {
            "sentiment": "positive",
            "score": 0.7
        }
        mock_get.return_value.status_code = 200
        
        analyzer = SentimentAnalyzer()
        
        score = analyzer.analisar_sentimento()
        
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0
    
    def test_processar_texto_sentiment(self, mock_config):
        """Testa processamento de texto para sentimento"""
        analyzer = SentimentAnalyzer()
        
        textos_positivos = [
            "Bitcoin is going to the moon!",
            "Great bullish momentum",
            "Excellent buying opportunity"
        ]
        
        textos_negativos = [
            "Bitcoin crash incoming",
            "Bearish market conditions",
            "Sell everything now"
        ]
        
        score_positivo = analyzer._processar_textos(textos_positivos)
        score_negativo = analyzer._processar_textos(textos_negativos)
        
        assert isinstance(score_positivo, float)
        assert isinstance(score_negativo, float)
        assert score_positivo > score_negativo
    
    def test_cache_sentiment(self, mock_config):
        """Testa cache de sentimento"""
        analyzer = SentimentAnalyzer()
        
        analyzer.cache_sentiment["BTC"] = {
            "score": 0.5,
            "timestamp": datetime.now(),
            "fonte": "twitter"
        }
        
        score = analyzer._obter_cache_sentiment("BTC")
        
        assert score == 0.5


class TestAprendizadoContinuoAbrangente:
    """Testes abrangentes para aprendizado contínuo"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_ia_config.return_value = Mock(
            rl_ativo=True,
            modelo_path="models/rl/",
            update_frequency=100
        )
        return config
    
    def test_inicializacao_aprendizado_continuo(self, mock_config):
        """Testa inicialização do aprendizado contínuo"""
        aprendizado = AprendizadoContinuo()
        
        assert hasattr(aprendizado, 'modelo_rl')
        assert hasattr(aprendizado, 'historico_acoes')
    
    def test_treinar_modelo_com_trades(self, mock_config):
        """Testa treinamento do modelo com trades"""
        aprendizado = AprendizadoContinuo()
        
        trades = [
            Trade(id="1", bot="swing", symbol="BTC/USDT", side="buy", 
                  amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=150),
            Trade(id="2", bot="swing", symbol="BTC/USDT", side="sell", 
                  amount=0.01, price=49800, timestamp=datetime.now(), caso_uso=1, pnl=-100)
        ]
        
        metricas = {
            "win_rate": 0.5,
            "profit_factor": 1.5,
            "sharpe_ratio": 0.8
        }
        
        resultado = aprendizado.treinar_modelo(trades, metricas)
        
        assert resultado is not None
        assert isinstance(resultado, dict)
    
    def test_extrair_features_trades(self, mock_config):
        """Testa extração de features dos trades"""
        aprendizado = AprendizadoContinuo()
        
        trades = [
            Trade(id="1", bot="mean_reversion", symbol="BTC/USDT", side="buy", 
                  amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=80),
            Trade(id="2", bot="mean_reversion", symbol="BTC/USDT", side="sell", 
                  amount=0.01, price=50080, timestamp=datetime.now(), caso_uso=1, pnl=40)
        ]
        
        features = aprendizado._extrair_features(trades)
        
        assert isinstance(features, np.ndarray)
        assert len(features.shape) == 2  # Matrix de features
        assert features.shape[0] == len(trades)
    
    def test_calcular_reward_trades(self, mock_config):
        """Testa cálculo de reward dos trades"""
        aprendizado = AprendizadoContinuo()
        
        trade_positivo = Trade(id="1", bot="scalping", symbol="BTC/USDT", side="buy", 
                              amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=120)
        
        trade_negativo = Trade(id="2", bot="scalping", symbol="BTC/USDT", side="sell", 
                              amount=0.01, price=49900, timestamp=datetime.now(), caso_uso=1, pnl=-80)
        
        reward_positivo = aprendizado._calcular_reward(trade_positivo)
        reward_negativo = aprendizado._calcular_reward(trade_negativo)
        
        assert isinstance(reward_positivo, float)
        assert isinstance(reward_negativo, float)
        assert reward_positivo > reward_negativo
    
    def test_atualizar_politica(self, mock_config):
        """Testa atualização da política"""
        aprendizado = AprendizadoContinuo()
        
        experiencias = [
            {"state": [0.1, 0.2, 0.3], "action": 1, "reward": 0.5, "next_state": [0.2, 0.3, 0.4]},
            {"state": [0.2, 0.3, 0.4], "action": 0, "reward": -0.2, "next_state": [0.1, 0.2, 0.3]}
        ]
        
        resultado = aprendizado._atualizar_politica(experiencias)
        
        assert resultado is not None
        assert isinstance(resultado, dict)


class TestMotorIAIntegracao:
    """Testes de integração do motor de IA"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_ia_config.return_value = Mock(
            modelo_path="models/",
            ia_habilitada=True,
            auto_tuning=True,
            sentiment_analysis=True,
            aprendizado_continuo=True
        )
        return config
    
    @pytest.mark.asyncio
    async def test_inicializacao_motor_ia_completo(self, mock_config):
        """Testa inicialização completa do motor de IA"""
        with patch('pathlib.Path.mkdir'):
            motor = MotorIA(mock_config)
            await motor.inicializar()
            
            assert hasattr(motor, 'gerador_sinais')
            assert hasattr(motor, 'auto_tuner')
            assert hasattr(motor, 'sentiment_analyzer')
            assert hasattr(motor, 'aprendizado_continuo')
    
    @pytest.mark.asyncio
    async def test_analisar_mercado_integrado(self, mock_config):
        """Testa análise integrada do mercado"""
        with patch('pathlib.Path.mkdir'):
            motor = MotorIA(mock_config)
            await motor.inicializar()
            
            dados_market = {
                "symbol": "BTC/USDT",
                "ohlcv": [[i, 50000, 50100, 49900, 50000, 100] for i in range(20)],
                "ticker": {"last": 50000}
            }
            
            with patch.object(motor.sentiment_analyzer, 'analisar_sentimento', return_value=0.3):
                resultado = await motor.analisar_mercado(dados_market)
                
                assert resultado is not None
                assert "sinal" in resultado
                assert "sentiment" in resultado
    
    @pytest.mark.asyncio
    async def test_otimizar_estrategia_integrada(self, mock_config):
        """Testa otimização integrada de estratégia"""
        with patch('pathlib.Path.mkdir'):
            motor = MotorIA(mock_config)
            await motor.inicializar()
            
            estrategia = "arbitragem"
            historico = [
                Trade(id="1", bot="arbitragem", symbol="BTC/USDT", side="buy", 
                      amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=90)
            ]
            
            resultado = await motor.otimizar_estrategia(estrategia, historico)
            
            assert resultado is not None
            assert isinstance(resultado, dict)
    
    @pytest.mark.asyncio
    async def test_treinar_modelo_continuo_integrado(self, mock_config):
        """Testa treinamento contínuo integrado"""
        with patch('pathlib.Path.mkdir'):
            motor = MotorIA(mock_config)
            await motor.inicializar()
            
            logs_trades = [
                Trade(id="1", bot="grid", symbol="BTC/USDT", side="buy", 
                      amount=0.01, price=50000, timestamp=datetime.now(), caso_uso=1, pnl=60)
            ]
            
            metricas = {"win_rate": 0.6, "profit_factor": 1.2}
            
            resultado = await motor.treinar_modelo_continuo(logs_trades, metricas)
            
            assert resultado is not None
            assert isinstance(resultado, dict)
