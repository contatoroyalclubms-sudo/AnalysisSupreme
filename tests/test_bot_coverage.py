"""
Testes específicos para aumentar cobertura dos bots
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.core.configuracao import Configuracao
from src.bots.arbitragem import BotArbitragem
from src.bots.grid import BotGrid
from src.bots.momentum import BotMomentum
from src.bots.scalping import BotScalping
from src.bots.mean_reversion import BotMeanReversion
from src.bots.swing import BotSwing


class TestBotCoverage:
    """Testes para aumentar cobertura dos bots"""

    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.paper_mode = True
        config.get_bot_config.return_value = Mock()
        config.get_bot_config.return_value.ativo = True
        config.get_bot_config.return_value.parametros = {"spread_min": 0.1, "volume_min": 1000}
        config.get_bot_config.return_value.casos_uso = {
            1: {"tipo": "alta_volatilidade", "spread_min": 0.2},
            2: {"tipo": "baixa_volatilidade", "spread_min": 0.1},
            3: {"tipo": "lateral", "spread_min": 0.15},
        }
        config.get_exchange_config.return_value = Mock(nome="binance", api_key="test", api_secret="test", sandbox=True)
        config.get_cache_config.return_value = {"l1_max_size_mb": 512, "redis_url": "redis://localhost:6379"}
        return config

    @pytest.fixture
    def mock_monitor(self):
        monitor = Mock()
        monitor.registrar_bot = AsyncMock()
        monitor.registrar_trade = AsyncMock()
        monitor.salvar_metricas_bot = AsyncMock()
        return monitor

    @pytest.fixture
    def mock_motor_ia(self):
        motor = Mock()
        motor.analisar_mercado = AsyncMock(return_value={"sinal": "comprar", "confidence": 0.8, "preco_entrada": 50000})
        return motor

    @pytest.mark.asyncio
    async def test_arbitragem_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de arbitragem de forma abrangente"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()
        assert bot.ativo == True
        assert bot.nome == "arbitragem"

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            params = bot.get_parametros_caso_uso(caso_uso)
            assert isinstance(params, dict)

        intervalo = bot.get_intervalo_execucao()
        assert isinstance(intervalo, int)
        assert intervalo > 0

        with patch.object(bot.exchange_manager, "get_ticker") as mock_ticker:
            mock_ticker.return_value = {"last": 50000, "bid": 49999, "ask": 50001}
            analise = await bot.analisar_mercado("BTC/USDT")
            assert isinstance(analise, dict)

        with patch.object(bot.exchange_manager, "get_ticker") as mock_ticker:
            mock_ticker.return_value = {"last": 50000}
            trade = await bot.executar_trade("BTC/USDT", "buy", 0.01, caso_uso=1)
            assert trade is not None
            assert trade.bot == "arbitragem"

        assert bot.get_total_trades() >= 0
        assert isinstance(bot.get_pnl_total(), (int, float))
        assert bot.get_status() in ["ativo", "inativo", "idle"]

        await bot.finalizar()
        assert bot.ativo == False

    @pytest.mark.asyncio
    async def test_grid_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de grid trading de forma abrangente"""
        bot = BotGrid(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)

        assert bot.get_intervalo_execucao() > 0

        with patch.object(bot.exchange_manager, "get_ohlcv") as mock_ohlcv:
            mock_ohlcv.return_value = [[1640995200000, 50000, 50100, 49900, 50050, 1000]]
            analise = await bot.analisar_mercado("BTC/USDT")
            assert isinstance(analise, dict)

        await bot.finalizar()

    @pytest.mark.asyncio
    async def test_momentum_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de momentum de forma abrangente"""
        bot = BotMomentum(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)

        ohlcv_data = []
        for i in range(50):
            price = 50000 + (i * 10)
            ohlcv_data.append([1640995200000 + i * 60000, price, price + 100, price - 50, price + 50, 1000])

        analise_tecnica = bot._analisar_tecnico(ohlcv_data)
        assert isinstance(analise_tecnica, dict)
        assert "sma_20" in analise_tecnica
        assert "rsi" in analise_tecnica

        await bot.finalizar()

    @pytest.mark.asyncio
    async def test_scalping_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de scalping de forma abrangente"""
        bot = BotScalping(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)

        assert bot.get_intervalo_execucao() <= 60  # Should be fast

        closes = [50000 + i * 10 for i in range(20)]
        rsi = bot._calcular_rsi(closes)
        assert 0 <= rsi <= 100

        await bot.finalizar()

    @pytest.mark.asyncio
    async def test_mean_reversion_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de mean reversion de forma abrangente"""
        bot = BotMeanReversion(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)

        with patch.object(bot.exchange_manager, "get_orderbook") as mock_orderbook:
            mock_orderbook.return_value = {"bids": [[49999, 1.0], [49998, 2.0]], "asks": [[50001, 1.0], [50002, 2.0]]}
            analise = await bot.analisar_mercado("BTC/USDT")
            assert "orderbook" in analise

        await bot.finalizar()

    @pytest.mark.asyncio
    async def test_swing_comprehensive(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa bot de swing trading de forma abrangente"""
        bot = BotSwing(mock_config, mock_monitor, mock_motor_ia)

        await bot.inicializar()

        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)

        assert bot.get_intervalo_execucao() >= 300  # Should be slower

        ohlcv_data = []
        for i in range(100):
            price = 50000 + (i * 5)
            ohlcv_data.append([1640995200000 + i * 3600000, price, price + 200, price - 100, price + 100, 1000])  # Hourly data

        analise_tecnica = bot._analisar_tecnico(ohlcv_data)
        assert isinstance(analise_tecnica, dict)
        assert "tendencia" in analise_tecnica

        await bot.finalizar()

    @pytest.mark.asyncio
    async def test_all_bots_error_handling(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa tratamento de erros em todos os bots"""
        bots = [
            BotArbitragem(mock_config, mock_monitor, mock_motor_ia),
            BotGrid(mock_config, mock_monitor, mock_motor_ia),
            BotMomentum(mock_config, mock_monitor, mock_motor_ia),
            BotScalping(mock_config, mock_monitor, mock_motor_ia),
            BotMeanReversion(mock_config, mock_monitor, mock_motor_ia),
            BotSwing(mock_config, mock_monitor, mock_motor_ia),
        ]

        for bot in bots:
            await bot.inicializar()

            with patch.object(bot.exchange_manager, "get_ticker") as mock_ticker:
                mock_ticker.side_effect = Exception("API Error")
                analise = await bot.analisar_mercado("BTC/USDT")
                assert analise == {}  # Should return empty dict on error

            with patch.object(bot.exchange_manager, "get_ticker") as mock_ticker:
                mock_ticker.side_effect = Exception("Trade Error")
                trade = await bot.executar_trade("BTC/USDT", "buy", 0.01)
                assert trade is None  # Should return None on error

            await bot.finalizar()

    def test_bot_configuration_edge_cases(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa casos extremos de configuração dos bots"""
        mock_config.get_bot_config.return_value = None

        with pytest.raises(ValueError):
            BotArbitragem(mock_config, mock_monitor, mock_motor_ia)

        mock_config.get_bot_config.return_value = Mock()
        mock_config.get_bot_config.return_value.ativo = True
        mock_config.get_bot_config.return_value.parametros = {}
        mock_config.get_bot_config.return_value.casos_uso = {}

        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)
        params = bot.get_parametros_caso_uso(999)  # Non-existent case
        assert params == {}

    @pytest.mark.asyncio
    async def test_bot_technical_analysis_edge_cases(self, mock_config, mock_monitor, mock_motor_ia):
        """Testa casos extremos da análise técnica"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_motor_ia)
        await bot.inicializar()

        empty_ohlcv = []
        analise = bot._analisar_tecnico(empty_ohlcv)
        assert analise == {}

        minimal_ohlcv = [[1640995200000, 50000, 50000, 50000, 50000, 1000]]
        analise = bot._analisar_tecnico(minimal_ohlcv)
        assert analise == {}

        same_prices = [50000] * 20
        rsi = bot._calcular_rsi(same_prices)
        assert rsi == 100.0  # All gains, no losses

        few_prices = [50000, 50100]
        rsi = bot._calcular_rsi(few_prices)
        assert rsi == 50.0  # Default value

        await bot.finalizar()
