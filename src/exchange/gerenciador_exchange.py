"""
Gerenciador de exchanges para trading com alta performance
"""

import ccxt
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.configuracao import Configuracao
from .websocket_pool import WebSocketPool
from ..core.engine.cache_intelligence import CacheIntelligence
from ..utils.circuit_breaker import ExchangeCircuitBreakers
from ..utils.kpis import GerenciadorKPIs

logger = logging.getLogger(__name__)

class GerenciadorExchange:
    """Gerenciador de conexões com exchanges com alta performance"""
    
    def __init__(self, config: Configuracao):
        self.config = config
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.exchange_principal = None
        
        self.websocket_pool = WebSocketPool(max_connections_per_exchange=5)
        cache_config = config.get_cache_config()
        l1_max_size_mb = cache_config.get('l1_max_size_mb', 512) if isinstance(cache_config, dict) else 512
        self.cache = CacheIntelligence(l1_max_size_mb)
        self.circuit_breakers = ExchangeCircuitBreakers()
        self.kpi_manager = GerenciadorKPIs()
        
        self.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'websocket_messages': 0,
            'circuit_breaker_trips': 0
        }
    
    async def inicializar(self):
        """Inicializa conexões com exchanges e componentes de performance"""
        logger.info("Inicializando gerenciador de exchanges com alta performance")
        
        
        exchange_config = self.config.get_exchange_config("binance")
        if exchange_config:
            try:
                exchange = ccxt.binance({
                    'apiKey': exchange_config.api_key,
                    'secret': exchange_config.api_secret,
                    'sandbox': exchange_config.sandbox,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot'
                    }
                })
                
                if not self.config.paper_mode and exchange_config.api_key:
                    await exchange.load_markets()
                
                self.exchanges["binance"] = exchange
                self.exchange_principal = exchange
                logger.info("Exchange Binance configurada com sucesso")
                
                await self._setup_websockets()
                
            except Exception as e:
                logger.error(f"Erro ao configurar Binance: {e}")
                self.exchange_principal = self._criar_exchange_simulada()
        else:
            self.exchange_principal = self._criar_exchange_simulada()
        
        logger.info("Gerenciador de exchanges inicializado com alta performance")
    
    async def _setup_websockets(self):
        """Configura conexões WebSocket para dados em tempo real"""
        try:
            websocket_urls = {
                'binance': 'wss://stream.binance.com:9443/ws/btcusdt@ticker',
                'bybit': 'wss://stream.bybit.com/v5/public/spot',
                'okx': 'wss://ws.okx.com:8443/ws/v5/public'
            }
            
            for exchange, url in websocket_urls.items():
                if exchange in self.exchanges:
                    self.websocket_pool.register_handler(
                        exchange, 
                        self._handle_websocket_message
                    )
                    await self.websocket_pool.add_connection(exchange, url)
                    
        except Exception as e:
            logger.warning(f"Erro ao configurar WebSockets: {e}")
    
    async def _handle_websocket_message(self, data: dict):
        """Processa mensagens WebSocket recebidas"""
        try:
            self.performance_stats['websocket_messages'] += 1
            
            if 'stream' in data and 'data' in data:
                stream_data = data['data']
                symbol = stream_data.get('s', '').replace('USDT', '/USDT')
                
                if 'c' in stream_data:
                    ticker_data = {
                        'symbol': symbol,
                        'last': float(stream_data['c']),
                        'bid': float(stream_data.get('b', stream_data['c'])),
                        'ask': float(stream_data.get('a', stream_data['c'])),
                        'volume': float(stream_data.get('v', 0)),
                        'timestamp': datetime.now().timestamp()
                    }
                    
                    cache_key = f"ticker_{symbol}"
                    await self.cache.set_intelligent(cache_key, ticker_data, 'ticker')
                    
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WebSocket: {e}")
    
    def _criar_exchange_simulada(self):
        """Cria exchange simulada para paper trading"""
        class ExchangeSimulada:
            def __init__(self):
                self.markets = {
                    'BTC/USDT': {'symbol': 'BTC/USDT', 'base': 'BTC', 'quote': 'USDT'},
                    'ETH/USDT': {'symbol': 'ETH/USDT', 'base': 'ETH', 'quote': 'USDT'},
                    'ADA/USDT': {'symbol': 'ADA/USDT', 'base': 'ADA', 'quote': 'USDT'}
                }
            
            async def fetch_ticker(self, symbol):
                import random
                base_prices = {
                    'BTC/USDT': 45000,
                    'ETH/USDT': 3000,
                    'ADA/USDT': 0.5
                }
                base_price = base_prices.get(symbol, 100)
                variation = random.uniform(-0.02, 0.02)  # nosec B311
                price = base_price * (1 + variation)
                
                return {
                    'symbol': symbol,
                    'last': price,
                    'bid': price * 0.999,
                    'ask': price * 1.001,
                    'high': price * 1.05,
                    'low': price * 0.95,
                    'volume': random.uniform(1000, 10000)  # nosec B311
                }
            
            async def fetch_order_book(self, symbol, limit=10):
                ticker = await self.fetch_ticker(symbol)
                price = ticker['last']
                
                bids = []
                asks = []
                
                for i in range(limit):
                    bid_price = price * (1 - (i + 1) * 0.001)
                    ask_price = price * (1 + (i + 1) * 0.001)
                    volume = random.uniform(0.1, 10)  # nosec B311
                    
                    bids.append([bid_price, volume])
                    asks.append([ask_price, volume])
                
                return {
                    'bids': bids,
                    'asks': asks,
                    'timestamp': datetime.now().timestamp()
                }
            
            async def fetch_ohlcv(self, symbol, timeframe='1m', limit=100):
                ticker = await self.fetch_ticker(symbol)
                base_price = ticker['last']
                
                ohlcv = []
                current_time = datetime.now().timestamp() * 1000
                
                for i in range(limit):
                    timestamp = current_time - (limit - i) * 60000  # 1 minuto
                    
                    variation = random.uniform(-0.01, 0.01)  # nosec B311
                    open_price = base_price * (1 + variation)
                    close_price = open_price * (1 + random.uniform(-0.005, 0.005))  # nosec B311
                    high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))  # nosec B311
                    low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))  # nosec B311
                    volume = random.uniform(10, 1000)  # nosec B311
                    
                    ohlcv.append([timestamp, open_price, high_price, low_price, close_price, volume])
                
                return ohlcv
            
            async def create_order(self, symbol, type, side, amount, price=None):
                ticker = await self.fetch_ticker(symbol)
                execution_price = price if price else ticker['last']
                
                return {
                    'id': f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'type': type,
                    'side': side,
                    'amount': amount,
                    'price': execution_price,
                    'status': 'closed',
                    'timestamp': datetime.now().timestamp()
                }
        
        return ExchangeSimulada()
    
    async def get_ticker(self, symbol: str, exchange: str = None) -> Optional[Dict]:
        """Obtém ticker com cache e circuit breaker"""
        medicao_id = self.kpi_manager.iniciar_medicao_latencia("exchange", "get_ticker")
        
        try:
            self.performance_stats['total_requests'] += 1
            
            cache_key = f"ticker_{symbol}_{exchange or 'principal'}"
            cached_data = await self.cache.get_intelligent(cache_key, 'ticker')
            
            if cached_data:
                self.performance_stats['cache_hits'] += 1
                return cached_data
            
            exchange_name = exchange or 'principal'
            
            async def fetch_ticker_call():
                if exchange and exchange in self.exchanges:
                    return await self.exchanges[exchange].fetch_ticker(symbol)
                else:
                    return await self.exchange_principal.fetch_ticker(symbol)
            
            result = await self.circuit_breakers.call_with_breaker(
                exchange_name, fetch_ticker_call
            )
            
            if result:
                await self.cache.set_intelligent(cache_key, result, 'ticker')
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter ticker {symbol}: {e}")
            return None
        finally:
            latencia_ms = self.kpi_manager.finalizar_medicao_latencia(medicao_id)
    
    async def get_orderbook(self, symbol: str, limit: int = 10, exchange: str = None) -> Optional[Dict]:
        """Obtém order book com cache e circuit breaker"""
        try:
            self.performance_stats['total_requests'] += 1
            
            cache_key = f"orderbook_{symbol}_{limit}_{exchange or 'principal'}"
            cached_data = await self.cache.get_intelligent(cache_key, 'orderbook')
            
            if cached_data:
                self.performance_stats['cache_hits'] += 1
                return cached_data
            
            exchange_name = exchange or 'principal'
            
            async def fetch_orderbook_call():
                if exchange and exchange in self.exchanges:
                    return await self.exchanges[exchange].fetch_order_book(symbol, limit)
                else:
                    return await self.exchange_principal.fetch_order_book(symbol, limit)
            
            result = await self.circuit_breakers.call_with_breaker(
                exchange_name, fetch_orderbook_call
            )
            
            if result:
                await self.cache.set_intelligent(cache_key, result, 'orderbook')
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter orderbook {symbol}: {e}")
            return None
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100, 
                       exchange: str = None) -> List[List]:
        """Obtém dados OHLCV com cache"""
        try:
            self.performance_stats['total_requests'] += 1
            
            cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}_{exchange or 'principal'}"
            cached_data = await self.cache.get_intelligent(cache_key, 'ohlcv')
            
            if cached_data:
                self.performance_stats['cache_hits'] += 1
                return cached_data
            
            exchange_name = exchange or 'principal'
            
            async def fetch_ohlcv_call():
                if exchange and exchange in self.exchanges:
                    return await self.exchanges[exchange].fetch_ohlcv(symbol, timeframe, limit)
                else:
                    return await self.exchange_principal.fetch_ohlcv(symbol, timeframe, limit)
            
            result = await self.circuit_breakers.call_with_breaker(
                exchange_name, fetch_ohlcv_call
            )
            
            if result:
                await self.cache.set_intelligent(cache_key, result, 'ohlcv')
            
            return result or []
            
        except Exception as e:
            logger.error(f"Erro ao obter OHLCV {symbol}: {e}")
            return []
    
    async def create_order(self, symbol: str, order_type: str, side: str, 
                          amount: float, price: float = None, exchange: str = None) -> Optional[Dict]:
        """Cria ordem com circuit breaker"""
        try:
            if self.config.paper_mode:
                ticker = await self.get_ticker(symbol, exchange)
                execution_price = price if price else ticker['last'] if ticker else 0
                
                return {
                    'id': f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'symbol': symbol,
                    'type': order_type,
                    'side': side,
                    'amount': amount,
                    'price': execution_price,
                    'status': 'closed',
                    'timestamp': datetime.now().timestamp()
                }
            else:
                exchange_name = exchange or 'principal'
                
                async def create_order_call():
                    if exchange and exchange in self.exchanges:
                        return await self.exchanges[exchange].create_order(symbol, order_type, side, amount, price)
                    else:
                        return await self.exchange_principal.create_order(symbol, order_type, side, amount, price)
                
                return await self.circuit_breakers.call_with_breaker(
                    exchange_name, create_order_call
                )
                    
        except Exception as e:
            logger.error(f"Erro ao criar ordem: {e}")
            return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        cache_stats = self.cache.get_stats()
        circuit_states = self.circuit_breakers.get_all_states()
        
        return {
            'requests': self.performance_stats,
            'cache': cache_stats,
            'circuit_breakers': circuit_states,
            'websocket_pool': {
                'connections': len(self.websocket_pool.connections),
                'cache_size': len(self.websocket_pool.data_cache)
            }
        }
    
    async def finalizar(self):
        """Finaliza conexões com exchanges e componentes de performance"""
        logger.info("Finalizando gerenciador de exchanges")
        
        await self.websocket_pool.close_all()
        await self.cache.shutdown_intelligence()
        
        for exchange in self.exchanges.values():
            if hasattr(exchange, 'close'):
                try:
                    await exchange.close()
                except:  # nosec
                    pass  # nosec
        
        self.exchanges.clear()
        self.exchange_principal = None
        
        logger.info("Gerenciador de exchanges finalizado")
