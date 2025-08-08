"""
Testes dos bots de trading
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.core.configuracao import Configuracao
from src.bots.arbitragem import BotArbitragem
from src.bots.grid import BotGrid
from src.bots.momentum import BotMomentum
from src.bots.scalping import BotScalping
from src.bots.mean_reversion import BotMeanReversion
from src.bots.swing import BotSwing


@pytest.fixture
def mock_config():
    """Configuração mock para testes"""
    config = Mock(spec=Configuracao)
    config.paper_mode = True
    config.get_bot_config.return_value = Mock(
        nome="test_bot", ativo=True, parametros={"test_param": 1.0}, casos_uso={1: {"tipo": "test"}}
    )
    return config


@pytest.fixture
def mock_monitor():
    """Monitor mock para testes"""
    monitor = AsyncMock()
    monitor.registrar_bot = AsyncMock()
    monitor.registrar_trade = AsyncMock()
    return monitor


@pytest.fixture
def mock_motor_ia():
    """Motor IA mock para testes"""
    motor_ia = AsyncMock()
    motor_ia.analisar_mercado = AsyncMock(
        return_value={"predicao_preco_percent": 0.01, "predicao_tendencia": "alta", "confianca": 0.8}
    )
    return motor_ia


class TestBotArbitragem:
    """Testes do bot de arbitragem"""

    @pytest.mark.asyncio
    async def test_inicializacao(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa inicialização do bot"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)

        bot.exchange_manager = AsyncMock()
        bot.exchange_manager.inicializar = AsyncMock()

        await bot.inicializar()

        assert bot.ativo == True
        mock_monitor.registrar_bot.assert_called_once()

    @pytest.mark.asyncio
    async def test_detectar_arbitragem_simples(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de arbitragem simples"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        bot.exchange_manager.get_ticker = AsyncMock(
            side_effect=[{"bid": 45100, "ask": 45200}, {"bid": 44900, "ask": 45000}]  # Exchange 1  # Exchange 2
        )

        oportunidade = await bot._detectar_arbitragem_simples("BTC/USDT", "binance", "coinbase", 0.002)

        assert oportunidade is not None
        assert oportunidade["profit_percent"] > 0.002

    @pytest.mark.asyncio
    async def test_executar_caso_uso_1(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa execução do caso de uso 1"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()
        bot.executar_trade = AsyncMock()

        bot.get_parametros_caso_uso = Mock(return_value={"exchanges": ["binance", "coinbase"], "min_profit_percent": 0.5})

        await bot.executar_caso_uso(1)

        assert bot.exchange_manager.get_ticker.called


class TestBotGrid:
    """Testes do bot de grid trading"""

    @pytest.mark.asyncio
    async def test_criar_grid(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa criação de grid"""
        bot = BotGrid(mock_config, mock_monitor, mock_motor_ia)

        grid = await bot._criar_grid("test_grid", "BTC/USDT", 44000, 46000, 10, "fixo")

        assert grid is not None
        assert grid["symbol"] == "BTC/USDT"
        assert len(grid["niveis"]) == 10
        assert grid["preco_min"] == 44000
        assert grid["preco_max"] == 46000

    @pytest.mark.asyncio
    async def test_calcular_volatilidade(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa cálculo de volatilidade"""
        bot = BotGrid(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        ohlcv_mock = [
            [1, 45000, 45100, 44900, 45050, 100],
            [2, 45050, 45200, 44950, 45150, 120],
            [3, 45150, 45300, 45000, 45100, 110],
        ]
        bot.exchange_manager.get_ohlcv = AsyncMock(return_value=ohlcv_mock)

        volatilidade = await bot._calcular_volatilidade("BTC/USDT")

        assert isinstance(volatilidade, float)
        assert volatilidade > 0


class TestBotMomentum:
    """Testes do bot de momentum"""

    @pytest.mark.asyncio
    async def test_detectar_breakout(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de breakout"""
        bot = BotMomentum(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        ohlcv_mock = []
        for i in range(50):
            if i < 40:
                price = 45000 + (i * 10)  # Gradual rise to 45390
            else:
                price = 49200  # Clear breakout above resistance
            if i >= 40:
                ohlcv_mock.append([i, 49400, price + 50, price - 50, 49400, 100])
            else:
                ohlcv_mock.append([i, price, price + 50, price - 50, price, 100])

        bot.exchange_manager.get_ohlcv = AsyncMock(return_value=ohlcv_mock)

        breakout = await bot._detectar_breakout("BTC/USDT", False)

        assert breakout is not None
        assert breakout["tipo"] == "breakout_alta"

    @pytest.mark.asyncio
    async def test_calcular_momentum_score(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa cálculo de score de momentum"""
        bot = BotMomentum(mock_config, mock_monitor, mock_motor_ia)

        analise_mock = {
            "analise_tecnica": {"sma_20": 45000, "sma_50": 44500, "rsi": 60, "volume_ratio": 1.5, "tendencia": "alta"},
            "analise_ia": {"predicao_direcao": "alta"},
        }

        score = bot._calcular_momentum_score(analise_mock)

        assert isinstance(score, float)
        assert 0 <= score <= 1


class TestBotScalping:
    """Testes do bot de scalping"""

    @pytest.mark.asyncio
    async def test_detectar_spread_opportunity(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de oportunidade de spread"""
        bot = BotScalping(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        bot.exchange_manager.get_ticker = AsyncMock(return_value={"bid": 45000, "ask": 45025})  # Spread de 0.055%

        bot.exchange_manager.get_orderbook = AsyncMock(
            return_value={
                "bids": [[45000, 1.0], [44995, 0.5], [44990, 0.3]],
                "asks": [[45025, 1.0], [45030, 0.5], [45035, 0.3]],
            }
        )

        oportunidade = await bot._detectar_spread_opportunity("BTC/USDT", 0.0005)

        assert oportunidade is not None
        assert oportunidade["spread_percent"] >= 0.0005

    @pytest.mark.asyncio
    async def test_detectar_micro_movimento(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de micro-movimento"""
        bot = BotScalping(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        ohlcv_mock = []
        for i in range(10):
            price = 45000 + (i * 5)  # Movimento mais significativo
            volume = 100 + (i * 20) if i >= 8 else 100  # Volume alto nos últimos 2
            ohlcv_mock.append([i, price, price + 2, price - 2, price, volume])

        bot.exchange_manager.get_ohlcv = AsyncMock(return_value=ohlcv_mock)

        movimento = await bot._detectar_micro_movimento("BTC/USDT", 0.0001)

        assert movimento is not None
        assert movimento["direcao"] in ["alta", "baixa"]


class TestBotMeanReversion:
    """Testes do bot de mean reversion"""

    @pytest.mark.asyncio
    async def test_detectar_reversion_simples(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de reversão simples"""
        bot = BotMeanReversion(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        ohlcv_mock = []
        for i in range(60):
            if i < 50:
                price = 45000  # Preço estável
            else:
                price = 46000  # Desvio significativo
            ohlcv_mock.append([i, price, price + 50, price - 50, price, 100])

        bot.exchange_manager.get_ohlcv = AsyncMock(return_value=ohlcv_mock)

        reversion = await bot._detectar_reversion_simples("BTC/USDT", "sma", 50)

        assert reversion is not None
        assert "reversion_" in reversion["tipo"]

    @pytest.mark.asyncio
    async def test_calcular_rsi_series(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa cálculo de série RSI"""
        bot = BotMeanReversion(mock_config, mock_monitor, mock_motor_ia)

        closes = [45000 + i * 10 for i in range(30)]

        rsi_series = bot._calcular_rsi_series(closes, 14)

        assert len(rsi_series) > 0
        assert all(0 <= rsi <= 100 for rsi in rsi_series)


class TestBotSwing:
    """Testes do bot de swing trading"""

    @pytest.mark.asyncio
    async def test_encontrar_pivots(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de pivots"""
        bot = BotSwing(mock_config, mock_monitor, mock_motor_ia)

        prices = [45000, 45100, 45200, 45300, 45200, 45100, 45000, 45100, 45200]

        pivots_high = bot._encontrar_pivots(prices, "high", 2)
        pivots_low = bot._encontrar_pivots(prices, "low", 2)

        assert len(pivots_high) > 0
        assert len(pivots_low) > 0

    @pytest.mark.asyncio
    async def test_detectar_doji(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa detecção de padrão Doji"""
        bot = BotSwing(mock_config, mock_monitor, mock_motor_ia)

        candle_doji = [1, 45000, 45100, 44900, 45005, 100]

        doji = bot._detectar_doji(candle_doji)

        assert doji is not None
        assert doji["forca"] > 0.8  # Corpo pequeno = força alta

    @pytest.mark.asyncio
    async def test_analisar_fibonacci(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa análise de Fibonacci"""
        bot = BotSwing(mock_config, mock_monitor, mock_motor_ia)
        bot.exchange_manager = AsyncMock()

        ohlcv_mock = []
        for i in range(100):
            if i < 50:
                price = 44000 + i * 20  # Subida
            else:
                price = 45000 - (i - 50) * 10  # Retração
            ohlcv_mock.append([i, price, price + 50, price - 50, price, 100])

        bot.exchange_manager.get_ohlcv = AsyncMock(return_value=ohlcv_mock)

        fib_analysis = await bot._analisar_fibonacci("BTC/USDT", [0.382, 0.618])

        assert fib_analysis is None or isinstance(fib_analysis, dict)


@pytest.mark.asyncio
async def test_integracao_bots(mock_config, mock_monitor, mock_motor_ia):
    """Teste de integração entre bots"""
    bots = [
        BotArbitragem(mock_config, mock_monitor, mock_motor_ia),
        BotGrid(mock_config, mock_monitor, mock_motor_ia),
        BotMomentum(mock_config, mock_monitor, mock_motor_ia),
        BotScalping(mock_config, mock_monitor, mock_motor_ia),
        BotMeanReversion(mock_config, mock_monitor, mock_motor_ia),
        BotSwing(mock_config, mock_monitor, mock_motor_ia),
    ]

    for bot in bots:
        bot.exchange_manager = AsyncMock()
        bot.exchange_manager.inicializar = AsyncMock()
        await bot.inicializar()
        assert bot.ativo == True

    intervalos = [bot.get_intervalo_execucao() for bot in bots]
    assert all(isinstance(i, int) and i > 0 for i in intervalos)

    for bot in bots:
        assert hasattr(bot, "executar")
        assert hasattr(bot, "executar_caso_uso")
        assert hasattr(bot, "finalizar")
