"""
Classe base para todos os bots de trading
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.core.configuracao import Configuracao
from src.models.trade import Trade
from src.exchange.gerenciador_exchange import GerenciadorExchange
from src.utils.metricas import CalculadorMetricas

logger = logging.getLogger(__name__)


class BotBase(ABC):
    """Classe base para todos os bots de trading"""

    def __init__(self, config: Configuracao, monitor, motor_ia):
        self.config = config
        self.monitor = monitor
        self.motor_ia = motor_ia
        self.nome = self.__class__.__name__.replace("Bot", "").lower()

        self.ativo = False
        self.ultima_execucao: Optional[datetime] = None
        self.trades: List[Trade] = []
        self.posicoes_abertas: Dict[str, Any] = {}

        self.bot_config = config.get_bot_config(self.nome)
        if not self.bot_config:
            raise ValueError(f"Configuração não encontrada para bot {self.nome}")

        self.exchange_manager = GerenciadorExchange(config)
        self.calculador_metricas = CalculadorMetricas()

        self.logger = logging.getLogger(f"{__name__}.{self.nome}")

    async def inicializar(self):
        """Inicializa o bot"""
        self.logger.info(f"Inicializando bot {self.nome}")

        await self.exchange_manager.inicializar()
        self.ativo = True

        if self.monitor:
            await self.monitor.registrar_bot(self.nome)

        self.logger.info(f"Bot {self.nome} inicializado com sucesso")

    @abstractmethod
    async def executar(self):
        """Executa a lógica principal do bot"""
        pass

    @abstractmethod
    async def executar_caso_uso(self, caso_uso: int):
        """Executa um caso de uso específico"""
        pass

    @abstractmethod
    def get_intervalo_execucao(self) -> int:
        """Retorna intervalo entre execuções em segundos"""
        pass

    async def analisar_mercado(self, symbol: str) -> Dict[str, Any]:
        """Analisa o mercado para um símbolo"""
        try:
            ticker = await self.exchange_manager.get_ticker(symbol)
            orderbook = await self.exchange_manager.get_orderbook(symbol)
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1m", 100)

            analise_tecnica = self._analisar_tecnico(ohlcv)

            analise_ia = await self.motor_ia.analisar_mercado(symbol, ohlcv)

            return {
                "ticker": ticker,
                "orderbook": orderbook,
                "ohlcv": ohlcv,
                "analise_tecnica": analise_tecnica,
                "analise_ia": analise_ia,
                "timestamp": datetime.now(),
            }

        except Exception as e:
            self.logger.error(f"Erro ao analisar mercado para {symbol}: {e}")
            return {}

    def _analisar_tecnico(self, ohlcv: List[List]) -> Dict[str, Any]:
        """Análise técnica básica"""
        if len(ohlcv) < 20:
            return {}

        closes = [candle[4] for candle in ohlcv]
        volumes = [candle[5] for candle in ohlcv]

        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20

        rsi = self._calcular_rsi(closes)

        volume_medio = sum(volumes[-20:]) / 20
        volume_atual = volumes[-1]

        return {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi": rsi,
            "volume_ratio": volume_atual / volume_medio if volume_medio > 0 else 1,
            "preco_atual": closes[-1],
            "tendencia": "alta" if sma_20 > sma_50 else "baixa",
        }

    def _calcular_rsi(self, closes: List[float], periodo: int = 14) -> float:
        """Calcula RSI simplificado"""
        if len(closes) < periodo + 1:
            return 50.0

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-periodo:]]
        losses = [-d if d < 0 else 0 for d in deltas[-periodo:]]

        avg_gain = sum(gains) / periodo
        avg_loss = sum(losses) / periodo

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    async def executar_trade(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        caso_uso: int = 1,
    ) -> Optional[Trade]:
        """Executa um trade"""
        try:
            if self.config.paper_mode:
                trade_id = f"{self.nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                if price is None:
                    ticker = await self.exchange_manager.get_ticker(symbol)
                    price = ticker["last"] if ticker else 0

                trade = Trade(
                    id=trade_id,
                    bot=self.nome,
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    price=price,
                    timestamp=datetime.now(),
                    caso_uso=caso_uso,
                )

                self.trades.append(trade)
                self.logger.info(
                    f"Trade paper executado: {side} {amount} {symbol} @ {price}"
                )

            else:
                order = await self.exchange_manager.create_order(
                    symbol, "market", side, amount, price
                )

                if order:
                    trade = Trade(
                        id=order["id"],
                        bot=self.nome,
                        symbol=symbol,
                        side=side,
                        amount=amount,
                        price=order["price"],
                        timestamp=datetime.now(),
                        caso_uso=caso_uso,
                    )

                    self.trades.append(trade)
                    self.logger.info(
                        f"Trade real executado: {side} {amount} {symbol} @ {order['price']}"
                    )
                else:
                    self.logger.error("Falha ao executar trade real")
                    return None

            if self.monitor:
                await self.monitor.registrar_trade(trade)
            self.ultima_execucao = datetime.now()

            return trade

        except Exception as e:
            self.logger.error(f"Erro ao executar trade: {e}")
            return None

    def get_parametros_caso_uso(self, caso_uso: int) -> Dict[str, Any]:
        """Obtém parâmetros para um caso de uso específico"""
        if not self.bot_config:
            return {}

        casos_uso = getattr(self.bot_config, "casos_uso", {})
        if hasattr(casos_uso, "__contains__"):
            if caso_uso not in casos_uso:
                return {}
        else:
            casos_uso = {1: {}, 2: {}, 3: {}}

        parametros = (
            getattr(self.bot_config, "parametros", {}).copy()
            if hasattr(self.bot_config, "parametros")
            else {}
        )
        if caso_uso in casos_uso:
            parametros.update(casos_uso[caso_uso])

        return parametros

    def get_ultima_execucao(self) -> Optional[datetime]:
        """Retorna timestamp da última execução"""
        return self.ultima_execucao

    def get_total_trades(self) -> int:
        """Retorna total de trades executados"""
        return len(self.trades)

    def get_total_wins(self) -> int:
        """Retorna total de trades vencedores"""
        return len([t for t in self.trades if t.pnl > 0])

    def get_pnl_total(self) -> float:
        """Retorna PnL total"""
        return sum(t.pnl for t in self.trades)

    def get_status(self) -> str:
        """Retorna status atual do bot"""
        if not self.ativo:
            return "inativo"

        if self.ultima_execucao:
            tempo_desde_ultima = datetime.now() - self.ultima_execucao
            if tempo_desde_ultima > timedelta(minutes=10):
                return "idle"

        return "ativo"

    async def finalizar(self):
        """Finaliza o bot"""
        self.logger.info(f"Finalizando bot {self.nome}")

        self.ativo = False
        await self.exchange_manager.finalizar()

        metricas_finais = self.calculador_metricas.calcular_metricas_finais(self.trades)
        if self.monitor:
            await self.monitor.salvar_metricas_bot(self.nome, metricas_finais)

        self.logger.info(f"Bot {self.nome} finalizado")
