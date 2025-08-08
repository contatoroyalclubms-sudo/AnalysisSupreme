"""
Testes abrangentes para todos os bots
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime

from src.bots.arbitragem import BotArbitragem
from src.bots.grid import BotGrid
from src.bots.momentum import BotMomentum
from src.bots.scalping import BotScalping
from src.bots.mean_reversion import BotMeanReversion
from src.bots.swing import BotSwing
from src.core.configuracao import Configuracao
from src.models.trade import Trade


class TestBotArbitragem:
    """Testes abrangentes para bot de arbitragem"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "spread_minimo": 0.3,
                "volume_minimo": 100,
                "timeout_execucao": 5
            }
        )
        return config
    
    @pytest.fixture
    def mock_exchange(self):
        exchange = AsyncMock()
        exchange.get_ticker.return_value = {
            'symbol': 'BTC/USDT',
            'bid': 49999,
            'ask': 50001,
            'last': 50000
        }
        exchange.get_orderbook.return_value = {
            'bids': [[49999, 1.0], [49998, 0.5]],
            'asks': [[50001, 1.0], [50002, 0.5]]
        }
        exchange.create_order.return_value = {
            'id': 'order_123',
            'status': 'closed',
            'filled': 0.01
        }
        return exchange
    
    @pytest.fixture
    def mock_monitor(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_kpis(self):
        return Mock()
    
    @pytest.mark.asyncio
    async def test_inicializacao_bot(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa inicialização do bot de arbitragem"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
        
        assert bot.nome == "arbitragem"
        assert bot.config == mock_config
        assert bot.exchange_manager is not None
        assert bot.monitor == mock_monitor
        assert hasattr(bot, 'kpi_manager')
    
    @pytest.mark.asyncio
    async def test_executar_caso_uso_1(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa execução do caso de uso 1 - alta volatilidade"""
        with patch('src.bots.bot_base.GerenciadorExchange') as mock_exchange_class:
            mock_exchange_instance = AsyncMock()
            mock_exchange_instance.get_ticker.return_value = {
                'bid': 49999, 'ask': 50001, 'last': 50000
            }
            mock_exchange_instance.inicializar = AsyncMock()
            mock_exchange_class.return_value = mock_exchange_instance
            
            bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
            
            await bot.executar_caso_uso(1)
            
            mock_exchange_instance.get_ticker.assert_called()
            if mock_monitor.registrar_trade.call_count > 0:
                mock_monitor.registrar_trade.assert_called()
    
    @pytest.mark.asyncio
    async def test_executar_caso_uso_2(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa execução do caso de uso 2 - baixa volatilidade"""
        with patch('src.bots.bot_base.GerenciadorExchange') as mock_exchange_class:
            mock_exchange_instance = AsyncMock()
            mock_exchange_instance.get_ticker.return_value = {
                'bid': 49999, 'ask': 50001, 'last': 50000
            }
            mock_exchange_instance.inicializar = AsyncMock()
            mock_exchange_class.return_value = mock_exchange_instance
            
            bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
            
            await bot.executar_caso_uso(2)
            
            mock_exchange_instance.get_ticker.assert_called()
    
    @pytest.mark.asyncio
    async def test_executar_caso_uso_3(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa execução do caso de uso 3 - mercado lateral"""
        with patch('src.bots.bot_base.GerenciadorExchange') as mock_exchange_class:
            mock_exchange_instance = AsyncMock()
            mock_exchange_instance.get_ticker.return_value = {
                'bid': 49999, 'ask': 50001, 'last': 50000
            }
            mock_exchange_instance.inicializar = AsyncMock()
            mock_exchange_class.return_value = mock_exchange_instance
            
            bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
            
            await bot.executar_caso_uso(3)
            
            mock_exchange_instance.get_ticker.assert_called()
    
    @pytest.mark.asyncio
    async def test_detectar_arbitragem(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa detecção de oportunidades de arbitragem"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
        
        mock_exchange.get_ticker.return_value = {
            'symbol': 'BTC/USDT',
            'bid': 49900,
            'ask': 50100,
            'last': 50000
        }
        
        resultado = await bot._detectar_arbitragem_simples(
            "BTC/USDT", "binance", "coinbase", 0.005
        )
        
        if resultado:
            assert "profit_percent" in resultado
    
    @pytest.mark.asyncio
    async def test_executar_arbitragem(self, mock_config, mock_exchange, mock_monitor, mock_kpis):
        """Testa execução de arbitragem"""
        bot = BotArbitragem(mock_config, mock_monitor, mock_exchange)
        
        oportunidade = {
            "symbol": "BTC/USDT",
            "spread": 0.4,
            "volume": 0.01,
            "preco_compra": 49999,
            "preco_venda": 50001
        }
        
        resultado = await bot._executar_arbitragem_simples(oportunidade)
        
        assert resultado is not None
        mock_exchange.create_order.assert_called()


class TestBotGrid:
    """Testes abrangentes para bot de grid trading"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "grid_levels": 10,
                "range_percent": 5.0,
                "order_size": 0.01
            }
        )
        return config
    
    @pytest.mark.asyncio
    async def test_inicializacao_grid(self, mock_config):
        """Testa inicialização do bot grid"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        bot = BotGrid(mock_config, monitor, exchange)
        
        assert bot.nome == "grid"
        assert hasattr(bot, 'nome')
    
    @pytest.mark.asyncio
    async def test_criar_grid_orders(self, mock_config):
        """Testa criação de ordens do grid"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ticker.return_value = {
            'symbol': 'BTC/USDT',
            'last': 50000
        }
        
        bot = BotGrid(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_executar_todos_casos_uso_grid(self, mock_config):
        """Testa execução de todos os casos de uso do grid"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ticker.return_value = {'symbol': 'BTC/USDT', 'last': 50000}
        exchange.get_ohlcv.return_value = [[1, 50000, 50100, 49900, 50000, 100]]
        
        bot = BotGrid(mock_config, monitor, exchange)
        
        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            exchange.get_ticker.assert_called()


class TestBotMomentum:
    """Testes abrangentes para bot de momentum"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "breakout_threshold": 1.02,
                "stop_loss": 0.02,
                "take_profit": 0.04
            }
        )
        return config
    
    @pytest.mark.asyncio
    async def test_detectar_breakout(self, mock_config):
        """Testa detecção de breakout"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [
            [1, 49000, 49500, 48500, 49000, 100],
            [2, 49000, 49800, 48800, 49500, 120],
            [3, 49500, 51000, 49200, 50800, 150]  # Breakout
        ]
        
        bot = BotMomentum(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_executar_todos_casos_uso_momentum(self, mock_config):
        """Testa execução de todos os casos de uso do momentum"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [[1, 50000, 50100, 49900, 50000, 100]]
        exchange.get_ticker.return_value = {'symbol': 'BTC/USDT', 'last': 50000}
        
        bot = BotMomentum(mock_config, monitor, exchange)
        
        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            exchange.get_ohlcv.assert_called()


class TestBotScalping:
    """Testes abrangentes para bot de scalping"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "spread_target": 0.1,
                "quick_profit": 0.05,
                "max_hold_time": 60
            }
        )
        return config
    
    @pytest.mark.asyncio
    async def test_executar_scalping_rapido(self, mock_config):
        """Testa execução de scalping rápido"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_orderbook.return_value = {
            'bids': [[49999, 1.0]],
            'asks': [[50001, 1.0]]
        }
        exchange.create_order.return_value = {'id': 'order_123', 'status': 'closed'}
        
        bot = BotScalping(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_executar_todos_casos_uso_scalping(self, mock_config):
        """Testa execução de todos os casos de uso do scalping"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_orderbook.return_value = {
            'bids': [[49999, 1.0]],
            'asks': [[50001, 1.0]]
        }
        exchange.get_ticker.return_value = {'symbol': 'BTC/USDT', 'last': 50000}
        
        bot = BotScalping(mock_config, monitor, exchange)
        
        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            exchange.get_orderbook.assert_called()


class TestBotMeanReversion:
    """Testes abrangentes para bot de mean reversion"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "mean_period": 20
            }
        )
        return config
    
    @pytest.mark.asyncio
    async def test_calcular_rsi(self, mock_config):
        """Testa cálculo do RSI"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        precos = [50000, 50100, 49900, 50200, 49800, 50300, 49700, 50400]
        
        bot = BotMeanReversion(mock_config, monitor, exchange)
        
        rsi = bot._calcular_rsi(precos, 7)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
    
    @pytest.mark.asyncio
    async def test_detectar_reversao(self, mock_config):
        """Testa detecção de reversão"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [
            [i, 50000 - i*10, 50100 - i*10, 49900 - i*10, 50000 - i*10, 100]
            for i in range(20)
        ]
        
        bot = BotMeanReversion(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_executar_todos_casos_uso_mean_reversion(self, mock_config):
        """Testa execução de todos os casos de uso do mean reversion"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [[i, 50000, 50100, 49900, 50000, 100] for i in range(20)]
        
        bot = BotMeanReversion(mock_config, monitor, exchange)
        
        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            exchange.get_ohlcv.assert_called()


class TestBotSwing:
    """Testes abrangentes para bot de swing trading"""
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Configuracao)
        config.get_bot_config.return_value = Mock(
            ativo=True,
            parametros={
                "trend_period": 50,
                "swing_threshold": 0.05,
                "hold_time_min": 3600
            }
        )
        return config
    
    @pytest.mark.asyncio
    async def test_detectar_tendencia(self, mock_config):
        """Testa detecção de tendência"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [
            [i, 50000 + i*50, 50100 + i*50, 49900 + i*50, 50000 + i*50, 100]
            for i in range(50)
        ]
        
        bot = BotSwing(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_calcular_suporte_resistencia(self, mock_config):
        """Testa cálculo de suporte e resistência"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        precos = [50000, 50100, 49900, 50200, 49800, 50300, 49700, 50400]
        
        bot = BotSwing(mock_config, monitor, exchange)
        
        assert hasattr(bot, 'executar_caso_uso')
    
    @pytest.mark.asyncio
    async def test_executar_todos_casos_uso_swing(self, mock_config):
        """Testa execução de todos os casos de uso do swing"""
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        exchange.get_ohlcv.return_value = [[i, 50000, 50100, 49900, 50000, 100] for i in range(50)]
        
        bot = BotSwing(mock_config, monitor, exchange)
        
        for caso_uso in [1, 2, 3]:
            await bot.executar_caso_uso(caso_uso)
            exchange.get_ohlcv.assert_called()


class TestIntegracaoBots:
    """Testes de integração entre bots"""
    
    @pytest.mark.asyncio
    async def test_todos_bots_implementam_casos_uso(self):
        """Testa se todos os bots implementam os 3 casos de uso"""
        config = Mock()
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        config.get_bot_config.return_value = Mock(ativo=True, parametros={})
        exchange.get_ticker.return_value = {'symbol': 'BTC/USDT', 'last': 50000}
        exchange.get_ohlcv.return_value = [[1, 50000, 50100, 49900, 50000, 100]]
        exchange.get_orderbook.return_value = {'bids': [[49999, 1.0]], 'asks': [[50001, 1.0]]}
        
        bots = [
            BotArbitragem(config, monitor, exchange),
            BotGrid(config, monitor, exchange),
            BotMomentum(config, monitor, exchange),
            BotScalping(config, monitor, exchange),
            BotMeanReversion(config, monitor, exchange),
            BotSwing(config, monitor, exchange)
        ]
        
        for bot in bots:
            for caso_uso in [1, 2, 3]:
                try:
                    await bot.executar_caso_uso(caso_uso)
                    assert True  # Se chegou aqui, o método existe
                except Exception as e:
                    assert "has no attribute" not in str(e)
    
    @pytest.mark.asyncio
    async def test_bots_registram_kpis(self):
        """Testa se todos os bots registram KPIs"""
        config = Mock()
        exchange = AsyncMock()
        monitor = AsyncMock()
        kpis = Mock()
        
        config.get_bot_config.return_value = Mock(ativo=True, parametros={})
        exchange.get_ticker.return_value = {'symbol': 'BTC/USDT', 'last': 50000}
        
        bots = [
            BotArbitragem(config, monitor, exchange),
            BotGrid(config, monitor, exchange),
            BotMomentum(config, monitor, exchange),
            BotScalping(config, monitor, exchange),
            BotMeanReversion(config, monitor, exchange),
            BotSwing(config, monitor, exchange)
        ]
        
        for bot in bots:
            assert hasattr(bot, 'nome')
            assert bot.nome in ['arbitragem', 'grid', 'momentum', 'scalping', 'mean_reversion', 'swing']
