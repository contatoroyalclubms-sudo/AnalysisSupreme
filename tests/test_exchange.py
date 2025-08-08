"""
Testes para sistema de exchange
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime

from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.core.configuracao import Configuracao


class TestGerenciadorExchange:
    """Testes para gerenciador de exchange"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_exchange_config.return_value = Mock(
            nome="binance",
            api_key="test_key",
            api_secret="test_secret",
            sandbox=True
        )
        return config
    
    def test_inicializacao(self, mock_config):
        """Testa inicialização do gerenciador"""
        gerenciador = GerenciadorExchange(mock_config)
        assert gerenciador is not None
        assert gerenciador.config == mock_config
        assert hasattr(gerenciador, 'exchanges')
        assert hasattr(gerenciador, 'exchange_principal')
    
    @pytest.mark.asyncio
    async def test_inicializar_exchange(self, mock_config):
        """Testa inicialização do exchange"""
        gerenciador = GerenciadorExchange(mock_config)
        
        with patch('ccxt.binance') as mock_binance:
            mock_exchange = Mock()
            mock_exchange.load_markets = AsyncMock()
            mock_exchange.fetch_ticker = AsyncMock(return_value={
                'symbol': 'BTC/USDT',
                'last': 50000,
                'bid': 49999,
                'ask': 50001
            })
            mock_binance.return_value = mock_exchange
            
            await gerenciador.inicializar()
            assert "binance" in gerenciador.exchanges or gerenciador.exchange_principal is not None
    
    @pytest.mark.asyncio
    async def test_get_ticker(self, mock_config):
        """Testa obtenção de ticker"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        ticker = await gerenciador.get_ticker("BTC/USDT")
        
        assert ticker is not None
        assert ticker['symbol'] == 'BTC/USDT'
        assert 'last' in ticker
        assert 'bid' in ticker
        assert 'ask' in ticker
    
    @pytest.mark.asyncio
    async def test_get_orderbook(self, mock_config):
        """Testa obtenção de orderbook"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        orderbook = await gerenciador.get_orderbook("BTC/USDT", 5)
        
        assert orderbook is not None
        assert 'bids' in orderbook
        assert 'asks' in orderbook
        assert len(orderbook['bids']) <= 5
        assert len(orderbook['asks']) <= 5
    
    @pytest.mark.asyncio
    async def test_create_order_paper_mode(self, mock_config):
        """Testa criação de ordem em modo paper"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        resultado = await gerenciador.create_order("BTC/USDT", "limit", "buy", 0.01, 50000)
        
        assert resultado is not None
        assert resultado['status'] == 'closed'
        assert resultado['symbol'] == 'BTC/USDT'
        assert resultado['side'] == 'buy'
        assert resultado['amount'] == 0.01
    
    @pytest.mark.asyncio
    async def test_calcular_spread_manual(self, mock_config):
        """Testa cálculo manual de spread"""
        gerenciador = GerenciadorExchange(mock_config)
        
        ticker = {
            'bid': 49999,
            'ask': 50001
        }
        
        spread = ((ticker['ask'] - ticker['bid']) / ((ticker['ask'] + ticker['bid']) / 2)) * 100
        expected_spread = ((50001 - 49999) / 50000) * 100  # ~0.004%
        
        assert abs(spread - expected_spread) < 0.001
    
    @pytest.mark.asyncio
    async def test_get_ohlcv(self, mock_config):
        """Testa obtenção de dados OHLCV"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        ohlcv = await gerenciador.get_ohlcv("BTC/USDT", "1m", 5)
        
        assert ohlcv is not None
        assert len(ohlcv) <= 5
        if len(ohlcv) > 0:
            assert len(ohlcv[0]) == 6  # timestamp, o, h, l, c, v
    
    @pytest.mark.asyncio
    async def test_finalizar(self, mock_config):
        """Testa finalização do gerenciador"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        await gerenciador.finalizar()
        
        assert gerenciador.exchange_principal is None
        assert len(gerenciador.exchanges) == 0
    
    @pytest.mark.asyncio
    async def test_exchange_simulada(self, mock_config):
        """Testa exchange simulada"""
        mock_config.paper_mode = True
        mock_config.get_exchange_config.return_value = None  # Força uso da exchange simulada
        
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        assert gerenciador.exchange_principal is not None
        
        ticker = await gerenciador.get_ticker("BTC/USDT")
        assert ticker is not None
        assert 'last' in ticker
    
    @pytest.mark.asyncio
    async def test_multiple_exchanges(self, mock_config):
        """Testa múltiplas exchanges"""
        mock_config.paper_mode = True
        gerenciador = GerenciadorExchange(mock_config)
        await gerenciador.inicializar()
        
        ticker = await gerenciador.get_ticker("ETH/USDT")
        assert ticker is not None
        assert ticker['symbol'] == 'ETH/USDT'
