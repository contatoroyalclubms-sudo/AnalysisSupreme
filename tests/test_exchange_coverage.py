"""
Testes específicos para aumentar cobertura do exchange manager
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.core.configuracao import Configuracao


class TestExchangeCoverage:
    """Testes para aumentar cobertura do exchange manager"""

    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.paper_mode = True
        config.get_exchange_config.return_value = Mock(
            nome="binance", api_key="test_key", api_secret="test_secret", sandbox=True
        )
        return config

    @pytest.mark.asyncio
    async def test_exchange_initialization_comprehensive(self, mock_config):
        """Testa inicialização completa do exchange"""
        gerenciador = GerenciadorExchange(mock_config)

        await gerenciador.inicializar()
        assert gerenciador.exchange_principal is not None

        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT"]
        for symbol in symbols:
            ticker = await gerenciador.get_ticker(symbol)
            assert ticker is not None
            assert ticker["symbol"] == symbol

        await gerenciador.finalizar()

    @pytest.mark.asyncio
    async def test_exchange_operations_comprehensive(self, mock_config):
        """Testa operações completas do exchange"""
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()

        ticker = await gerenciador.get_ticker("BTC/USDT")
        assert "last" in ticker
        assert "bid" in ticker
        assert "ask" in ticker
        assert "volume" in ticker

        for limit in [5, 10, 20]:
            orderbook = await gerenciador.get_orderbook("BTC/USDT", limit)
            assert "bids" in orderbook
            assert "asks" in orderbook
            assert len(orderbook["bids"]) <= limit
            assert len(orderbook["asks"]) <= limit

        timeframes = ["1m", "5m", "1h", "1d"]
        for timeframe in timeframes:
            ohlcv = await gerenciador.get_ohlcv("BTC/USDT", timeframe, 10)
            assert isinstance(ohlcv, list)
            if len(ohlcv) > 0:
                assert len(ohlcv[0]) == 6  # timestamp, o, h, l, c, v

        await gerenciador.finalizar()

    @pytest.mark.asyncio
    async def test_order_operations_comprehensive(self, mock_config):
        """Testa operações de ordem completas"""
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()

        order_types = ["market", "limit"]
        sides = ["buy", "sell"]

        for order_type in order_types:
            for side in sides:
                order = await gerenciador.create_order("BTC/USDT", order_type, side, 0.01, 50000)
                assert order is not None
                assert order["symbol"] == "BTC/USDT"
                assert order["side"] == side
                assert order["type"] == order_type

        await gerenciador.finalizar()

    @pytest.mark.asyncio
    async def test_exchange_error_handling(self, mock_config):
        """Testa tratamento de erros do exchange"""
        gerenciador = GerenciadorExchange(mock_config)

        ticker = await gerenciador.get_ticker("BTC/USDT")
        assert ticker is not None  # Should work in paper mode

        await gerenciador.inicializar()

        invalid_symbols = ["INVALID/USDT", "BTC/INVALID", ""]
        for symbol in invalid_symbols:
            ticker = await gerenciador.get_ticker(symbol)
            assert ticker is not None

        await gerenciador.finalizar()

    @pytest.mark.asyncio
    async def test_exchange_paper_mode_comprehensive(self, mock_config):
        """Testa modo paper completo"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()

        symbols = ["BTC/USDT", "ETH/USDT", "LTC/USDT"]

        for symbol in symbols:
            ticker = await gerenciador.get_ticker(symbol)
            assert ticker["symbol"] == symbol
            assert ticker["last"] > 0
            assert ticker["bid"] < ticker["ask"]

            orderbook = await gerenciador.get_orderbook(symbol, 10)
            assert len(orderbook["bids"]) > 0
            assert len(orderbook["asks"]) > 0

            ohlcv = await gerenciador.get_ohlcv(symbol, "1m", 5)
            assert len(ohlcv) > 0

            order = await gerenciador.create_order(symbol, "market", "buy", 0.01)
            assert order["status"] == "closed"

        await gerenciador.finalizar()

    @pytest.mark.asyncio
    async def test_exchange_real_mode_simulation(self, mock_config):
        """Testa simulação do modo real"""
        mock_config.paper_mode = False

        with patch("ccxt.binance") as mock_binance:
            mock_exchange = Mock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.fetch_ticker = AsyncMock(
                return_value={"symbol": "BTC/USDT", "last": 50000, "bid": 49999, "ask": 50001, "volume": 1000}
            )
            mock_exchange.fetch_order_book = AsyncMock(
                return_value={"bids": [[49999, 1.0], [49998, 2.0]], "asks": [[50001, 1.0], [50002, 2.0]]}
            )
            mock_exchange.fetch_ohlcv = AsyncMock(return_value=[[1640995200000, 50000, 50100, 49900, 50050, 1000]])
            mock_exchange.create_order = AsyncMock(
                return_value={
                    "id": "test_order_123",
                    "symbol": "BTC/USDT",
                    "side": "buy",
                    "amount": 0.01,
                    "price": 50000,
                    "status": "closed",
                }
            )
            mock_binance.return_value = mock_exchange

            gerenciador = GerenciadorExchange(mock_config)
            await gerenciador.inicializar()

            ticker = await gerenciador.get_ticker("BTC/USDT")
            assert ticker["symbol"] == "BTC/USDT"

            orderbook = await gerenciador.get_orderbook("BTC/USDT")
            assert "bids" in orderbook

            ohlcv = await gerenciador.get_ohlcv("BTC/USDT", "1m", 5)
            assert len(ohlcv) > 0

            order = await gerenciador.create_order("BTC/USDT", "market", "buy", 0.01)
            assert order["id"] == "test_order_123"

            await gerenciador.finalizar()

    def test_exchange_configuration_edge_cases(self, mock_config):
        """Testa casos extremos de configuração"""
        mock_config.get_exchange_config.return_value = None
        gerenciador = GerenciadorExchange(mock_config)
        assert gerenciador is not None

        exchanges = ["binance", "bybit", "okx"]
        for exchange in exchanges:
            mock_config.get_exchange_config.return_value = Mock(nome=exchange, api_key="test", api_secret="test", sandbox=True)
            gerenciador = GerenciadorExchange(mock_config)
            assert gerenciador is not None

    @pytest.mark.asyncio
    async def test_exchange_data_validation(self, mock_config):
        """Testa validação de dados do exchange"""
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()

        ticker = await gerenciador.get_ticker("BTC/USDT")
        required_fields = ["symbol", "last", "bid", "ask", "volume"]
        for field in required_fields:
            assert field in ticker
            assert ticker[field] is not None

        orderbook = await gerenciador.get_orderbook("BTC/USDT", 5)
        assert "bids" in orderbook
        assert "asks" in orderbook
        assert isinstance(orderbook["bids"], list)
        assert isinstance(orderbook["asks"], list)

        ohlcv = await gerenciador.get_ohlcv("BTC/USDT", "1m", 5)
        assert isinstance(ohlcv, list)
        if len(ohlcv) > 0:
            candle = ohlcv[0]
            assert len(candle) == 6
            assert all(isinstance(x, (int, float)) for x in candle)

        await gerenciador.finalizar()
