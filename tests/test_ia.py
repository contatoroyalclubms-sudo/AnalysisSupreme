"""
Testes para componentes de IA
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from datetime import datetime

from src.ia.motor_ia import (
    MotorIA,
    GeradorSinais,
    AutoTuner,
    SentimentAnalyzer,
    AprendizadoContinuo,
    Sinal,
)


class TestGeradorSinais:
    """Testes para GeradorSinais"""

    def test_inicializacao(self):
        """Testa inicialização do gerador de sinais"""
        gerador = GeradorSinais()
        assert gerador is not None

    def test_analisar_mercado(self):
        """Testa análise de mercado"""
        gerador = GeradorSinais()

        dados_market = {
            "ohlcv": [[1, 50000, 50100, 49900, 50050, 100] for _ in range(100)],
            "symbol": "BTC/USDT",
            "timeframe": "5m",
        }

        sinal = gerador.analisar_mercado(dados_market)
        assert isinstance(sinal, Sinal)
        assert sinal.acao in ["comprar", "vender", "parar"]
        assert 0 <= sinal.confidence <= 1

    def test_calcular_indicadores_tecnicos(self):
        """Testa cálculo de indicadores técnicos"""
        gerador = GeradorSinais()

        precos = [50000 + i * 10 for i in range(50)]

        indicadores = gerador._calcular_indicadores_tecnicos(precos)
        assert "sma_20" in indicadores
        assert "rsi" in indicadores
        assert "macd" in indicadores
        assert "bollinger_bands" in indicadores

    def test_combinar_sinais(self):
        """Testa combinação de sinais"""
        gerador = GeradorSinais()

        sinais_individuais = [
            {"acao": "comprar", "confidence": 0.7},
            {"acao": "comprar", "confidence": 0.6},
            {"acao": "vender", "confidence": 0.4},
            {"acao": "comprar", "confidence": 0.8},
        ]

        sinal_final = gerador._combinar_sinais(sinais_individuais)
        assert sinal_final["acao"] == "comprar"  # Maioria comprar
        assert sinal_final["confidence"] > 0.5


class TestAutoTuner:
    """Testes para AutoTuner"""

    def test_inicializacao(self):
        """Testa inicialização do auto tuner"""
        tuner = AutoTuner()
        assert tuner is not None

    def test_otimizar_parametros(self):
        """Testa otimização de parâmetros"""
        tuner = AutoTuner()

        estrategia = "momentum"
        historico = {
            "trades": [
                {"pnl": 100, "parametros": {"stop_loss": 0.02, "take_profit": 0.06}},
                {"pnl": -50, "parametros": {"stop_loss": 0.01, "take_profit": 0.03}},
                {"pnl": 200, "parametros": {"stop_loss": 0.025, "take_profit": 0.05}},
            ]
        }

        parametros_otimizados = tuner.otimizar_parametros(estrategia, historico)
        assert isinstance(parametros_otimizados, dict)
        assert "stop_loss" in parametros_otimizados
        assert "take_profit" in parametros_otimizados
        assert "position_size" in parametros_otimizados

    def test_algoritmo_genetico(self):
        """Testa algoritmo genético"""
        tuner = AutoTuner()

        def fitness_function(params):
            return params["stop_loss"] * 0.5 + params["take_profit"] * 0.3

        melhor_params = tuner._algoritmo_genetico(fitness_function, 10, 5)
        assert isinstance(melhor_params, dict)
        assert "stop_loss" in melhor_params
        assert "take_profit" in melhor_params

    def test_otimizacao_bayesiana(self):
        """Testa otimização bayesiana"""
        tuner = AutoTuner()

        historico_performance = [
            {"params": {"stop_loss": 0.02}, "score": 0.65},
            {"params": {"stop_loss": 0.015}, "score": 0.72},
            {"params": {"stop_loss": 0.025}, "score": 0.58},
        ]

        proximo_param = tuner._otimizacao_bayesiana(historico_performance)
        assert isinstance(proximo_param, dict)
        assert "stop_loss" in proximo_param


class TestSentimentAnalyzer:
    """Testes para SentimentAnalyzer"""

    def test_inicializacao(self):
        """Testa inicialização do analisador de sentimento"""
        analyzer = SentimentAnalyzer()
        assert analyzer is not None

    @patch("requests.get")
    def test_analisar_sentimento(self, mock_get):
        """Testa análise de sentimento"""
        analyzer = SentimentAnalyzer()

        mock_response = Mock()
        mock_response.json.return_value = {
            "articles": [
                {"title": "Bitcoin reaches new highs", "sentiment": "positive"},
                {"title": "Crypto market shows strong growth", "sentiment": "positive"},
                {"title": "Market volatility concerns", "sentiment": "negative"},
            ]
        }
        mock_get.return_value = mock_response

        score = analyzer.analisar_sentimento()
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0

    def test_analisar_twitter(self):
        """Testa análise de sentimento do Twitter"""
        analyzer = SentimentAnalyzer()

        tweets_mock = [
            "Bitcoin to the moon! 🚀",
            "Crypto market looking bullish",
            "Concerned about market volatility",
            "Great time to buy the dip!",
        ]

        with patch.object(analyzer, "_obter_tweets", return_value=tweets_mock):
            score = analyzer._analisar_twitter()
            assert isinstance(score, float)
            assert -1.0 <= score <= 1.0

    def test_analisar_reddit(self):
        """Testa análise de sentimento do Reddit"""
        analyzer = SentimentAnalyzer()

        posts_mock = [
            {"title": "Bitcoin analysis - very bullish", "score": 150},
            {"title": "Market crash incoming?", "score": -50},
            {"title": "Hodl strong!", "score": 200},
        ]

        with patch.object(analyzer, "_obter_posts_reddit", return_value=posts_mock):
            score = analyzer._analisar_reddit()
            assert isinstance(score, float)
            assert -1.0 <= score <= 1.0

    def test_analisar_noticias(self):
        """Testa análise de sentimento de notícias"""
        analyzer = SentimentAnalyzer()

        noticias_mock = [
            {
                "title": "Bitcoin adoption increases globally",
                "content": "Positive news...",
            },
            {"title": "Regulatory concerns for crypto", "content": "Negative news..."},
            {"title": "New crypto innovations", "content": "Positive developments..."},
        ]

        with patch.object(analyzer, "_obter_noticias", return_value=noticias_mock):
            score = analyzer._analisar_noticias()
            assert isinstance(score, float)
            assert -1.0 <= score <= 1.0


class TestAprendizadoContinuo:
    """Testes para AprendizadoContinuo"""

    def test_inicializacao(self):
        """Testa inicialização do aprendizado contínuo"""
        aprendizado = AprendizadoContinuo()
        assert aprendizado is not None

    def test_treinar_modelo(self):
        """Testa treinamento do modelo"""
        aprendizado = AprendizadoContinuo()

        logs_trades = [
            {
                "symbol": "BTC/USDT",
                "action": "buy",
                "price": 50000,
                "result": "win",
                "pnl": 100,
                "market_conditions": {"volatility": 0.02, "volume": 1000},
            },
            {
                "symbol": "BTC/USDT",
                "action": "sell",
                "price": 49000,
                "result": "loss",
                "pnl": -50,
                "market_conditions": {"volatility": 0.03, "volume": 800},
            },
        ]

        metricas = {"win_rate": 0.6, "avg_pnl": 25, "sharpe_ratio": 1.2}

        resultado = aprendizado.treinar_modelo(logs_trades, metricas)
        assert resultado is not None
        assert "modelo_atualizado" in resultado

    def test_extrair_features(self):
        """Testa extração de features"""
        aprendizado = AprendizadoContinuo()

        trade = {
            "symbol": "BTC/USDT",
            "action": "buy",
            "price": 50000,
            "market_conditions": {
                "volatility": 0.02,
                "volume": 1000,
                "rsi": 65,
                "macd": 0.5,
            },
        }

        features = aprendizado._extrair_features(trade)
        assert isinstance(features, np.ndarray)
        assert len(features) > 0

    def test_calcular_reward(self):
        """Testa cálculo de reward"""
        aprendizado = AprendizadoContinuo()

        trade_resultado = {
            "pnl": 100,
            "duration": 300,
            "max_drawdown": 0.01,
        }  # 5 minutos

        reward = aprendizado._calcular_reward(trade_resultado)
        assert isinstance(reward, float)
        assert reward != 0  # Deve ter algum valor de reward

    def test_atualizar_politica(self):
        """Testa atualização da política"""
        aprendizado = AprendizadoContinuo()

        experiencias = [
            {
                "state": np.array([0.02, 1000, 65, 0.5]),
                "action": 1,  # buy
                "reward": 0.8,
                "next_state": np.array([0.025, 1100, 70, 0.6]),
            }
        ]

        resultado = aprendizado._atualizar_politica(experiencias)
        assert resultado is not None
        assert "loss" in resultado or "success" in resultado


class TestMotorIA:
    """Testes para MotorIA principal"""

    @pytest.fixture
    def mock_config(self):
        config = Mock()
        config.get_config_ia.return_value = {
            "modelo_path": "models/",
            "training_enabled": True,
            "retrain_interval": 24,
        }
        return config

    @pytest.mark.asyncio
    async def test_inicializacao(self, mock_config):
        """Testa inicialização do motor de IA"""
        motor = MotorIA(mock_config)
        assert motor is not None
        assert motor.config == mock_config
        assert hasattr(motor, "gerador_sinais")
        assert hasattr(motor, "auto_tuner")
        assert hasattr(motor, "sentiment_analyzer")
        assert hasattr(motor, "aprendizado_continuo")

    @pytest.mark.asyncio
    async def test_inicializar(self, mock_config):
        """Testa inicialização dos componentes"""
        motor = MotorIA(mock_config)
        await motor.inicializar()
        assert motor.inicializado

    @pytest.mark.asyncio
    async def test_analisar_mercado(self, mock_config):
        """Testa análise de mercado"""
        motor = MotorIA(mock_config)
        await motor.inicializar()

        dados_mercado = {
            "symbol": "BTC/USDT",
            "ohlcv": [[1, 50000, 50100, 49900, 50050, 100] for _ in range(100)],
            "timeframe": "5m",
        }

        analise = await motor.analisar_mercado(dados_mercado)
        assert analise is not None
        assert "sinal_tecnico" in analise
        assert "sentimento" in analise
        assert "recomendacao" in analise

    @pytest.mark.asyncio
    async def test_otimizar_estrategia(self, mock_config):
        """Testa otimização de estratégia"""
        motor = MotorIA(mock_config)
        await motor.inicializar()

        estrategia = "momentum"
        historico = {
            "trades": [
                {"pnl": 100, "parametros": {"stop_loss": 0.02}},
                {"pnl": -50, "parametros": {"stop_loss": 0.01}},
            ]
        }

        parametros_otimizados = await motor.otimizar_estrategia(estrategia, historico)
        assert parametros_otimizados is not None
        assert isinstance(parametros_otimizados, dict)

    @pytest.mark.asyncio
    async def test_treinar_modelo_continuo(self, mock_config):
        """Testa treinamento contínuo"""
        motor = MotorIA(mock_config)
        await motor.inicializar()

        logs_trades = [
            {"symbol": "BTC/USDT", "action": "buy", "result": "win", "pnl": 100}
        ]

        metricas = {"win_rate": 0.6, "avg_pnl": 50}

        resultado = await motor.treinar_modelo_continuo(logs_trades, metricas)
        assert resultado is not None
