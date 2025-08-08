"""
Bot Scalping - Operações rápidas com pequenos lucros
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .bot_base import BotBase
from src.utils.kpis import GerenciadorKPIs


class BotScalping(BotBase):
    """Bot especializado em scalping"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.posicoes_scalping = {}
        self.orderbook_cache = {}

    def get_intervalo_execucao(self) -> int:
        """Intervalo de 15 segundos para scalping"""
        return 15

    async def executar(self):
        """Executa scalping em todos os casos de uso"""
        self.logger.info("Executando scalping")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico de scalping"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._scalping_spread(parametros)
        elif caso_uso == 2:
            await self._scalping_micro_movimentos(parametros)
        elif caso_uso == 3:
            await self._scalping_orderbook(parametros)

    async def _scalping_spread(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Scalping de spread bid/ask"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        min_spread = parametros.get("min_spread", 0.0005)

        for symbol in symbols:
            try:
                oportunidade = await self._detectar_spread_opportunity(
                    symbol, min_spread
                )
                if oportunidade:
                    await self._executar_scalping_spread(symbol, oportunidade, 1)
            except Exception as e:
                self.logger.error(f"Erro no scalping spread para {symbol}: {e}")

    async def _detectar_spread_opportunity(
        self, symbol: str, min_spread: float
    ) -> Optional[Dict]:
        """Detecta oportunidade de scalping no spread"""
        try:
            ticker = await self.exchange_manager.get_ticker(symbol)
            if not ticker:
                return None

            bid = ticker["bid"]
            ask = ticker["ask"]
            spread = ask - bid
            spread_percent = spread / ask

            if spread_percent >= min_spread:
                orderbook = await self.exchange_manager.get_orderbook(symbol, 5)
                if orderbook:
                    bid_volume = sum([level[1] for level in orderbook["bids"][:3]])
                    ask_volume = sum([level[1] for level in orderbook["asks"][:3]])

                    if bid_volume > 0.1 and ask_volume > 0.1:  # Liquidez mínima
                        return {
                            "bid": bid,
                            "ask": ask,
                            "spread": spread,
                            "spread_percent": spread_percent,
                            "bid_volume": bid_volume,
                            "ask_volume": ask_volume,
                        }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar spread opportunity: {e}")
            return None

    async def _executar_scalping_spread(
        self, symbol: str, oportunidade: Dict, caso_uso: int
    ):
        """Executa scalping no spread"""
        try:
            amount = 0.005  # Quantidade pequena para scalping

            bid_price = oportunidade["bid"]
            ask_price = oportunidade["ask"]

            self.logger.info(
                f"Scalping spread {symbol}: "
                f"Spread: {oportunidade['spread_percent']:.4%}"
            )

            trade_buy = await self.executar_trade(
                symbol, "buy", amount, bid_price, caso_uso=caso_uso
            )

            if trade_buy:
                trade_sell = await self.executar_trade(
                    symbol, "sell", amount, ask_price, caso_uso=caso_uso
                )

                if trade_sell:
                    pnl = (ask_price - bid_price) * amount
                    trade_buy.pnl = pnl / 2
                    trade_sell.pnl = pnl / 2

                    self.logger.info(f"Scalping spread executado. PnL: {pnl:.6f}")

        except Exception as e:
            self.logger.error(f"Erro ao executar scalping spread: {e}")

    async def _scalping_micro_movimentos(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Scalping de micro-movimentos"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        tick_size = parametros.get("tick_size", 0.0001)

        for symbol in symbols:
            try:
                movimento = await self._detectar_micro_movimento(symbol, tick_size)
                if movimento:
                    await self._executar_scalping_micro(symbol, movimento, 2)
            except Exception as e:
                self.logger.error(f"Erro no scalping micro para {symbol}: {e}")

    async def _detectar_micro_movimento(
        self, symbol: str, tick_size: float
    ) -> Optional[Dict]:
        """Detecta micro-movimentos de preço"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1m", 10)
            if len(ohlcv) < 5:
                return None

            closes = [candle[4] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]

            preco_atual = closes[-1]
            preco_anterior = closes[-2]
            movimento = preco_atual - preco_anterior
            movimento_percent = movimento / preco_anterior

            volume_atual = volumes[-1]
            volume_medio = sum(volumes[-5:]) / 5
            volume_ratio = volume_atual / volume_medio

            if abs(movimento_percent) >= tick_size and volume_ratio > 1.2:
                direcao = "alta" if movimento > 0 else "baixa"

                return {
                    "movimento": movimento,
                    "movimento_percent": movimento_percent,
                    "direcao": direcao,
                    "volume_ratio": volume_ratio,
                    "preco_atual": preco_atual,
                    "momentum": movimento_percent * volume_ratio,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar micro movimento: {e}")
            return None

    async def _executar_scalping_micro(
        self, symbol: str, movimento: Dict, caso_uso: int
    ):
        """Executa scalping em micro-movimentos"""
        try:
            amount = 0.003
            direcao = movimento["direcao"]

            self.logger.info(
                f"Micro-movimento detectado {symbol}: "
                f"{direcao} {movimento['movimento_percent']:.4%}"
            )

            if direcao == "alta":
                side = "buy"
                target_price = movimento["preco_atual"] * 1.0005  # 0.05% target
            else:
                side = "sell"
                target_price = movimento["preco_atual"] * 0.9995  # 0.05% target

            trade_entrada = await self.executar_trade(
                symbol, side, amount, caso_uso=caso_uso
            )

            if trade_entrada:
                self.posicoes_scalping[trade_entrada.id] = {
                    "target_price": target_price,
                    "entrada_time": datetime.now(),
                    "max_hold_time": 60,  # 1 minuto máximo
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                }

        except Exception as e:
            self.logger.error(f"Erro ao executar scalping micro: {e}")

    async def _scalping_orderbook(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Scalping baseado em order book"""
        symbols = ["BTC/USDT"]
        depth_levels = parametros.get("depth_levels", 5)

        for symbol in symbols:
            try:
                imbalance = await self._detectar_orderbook_imbalance(
                    symbol, depth_levels
                )
                if imbalance:
                    await self._executar_scalping_orderbook(symbol, imbalance, 3)
            except Exception as e:
                self.logger.error(f"Erro no scalping orderbook para {symbol}: {e}")

    async def _detectar_orderbook_imbalance(
        self, symbol: str, depth_levels: int
    ) -> Optional[Dict]:
        """Detecta desequilíbrio no order book"""
        try:
            orderbook = await self.exchange_manager.get_orderbook(symbol, depth_levels)
            if not orderbook:
                return None

            bid_volume = sum([level[1] for level in orderbook["bids"][:depth_levels]])
            ask_volume = sum([level[1] for level in orderbook["asks"][:depth_levels]])

            total_volume = bid_volume + ask_volume
            if total_volume == 0:
                return None

            bid_ratio = bid_volume / total_volume
            ask_ratio = ask_volume / total_volume

            threshold = 0.65  # 65% em uma direção

            if bid_ratio > threshold:
                return {
                    "tipo": "bid_dominance",
                    "bid_ratio": bid_ratio,
                    "ask_ratio": ask_ratio,
                    "bid_volume": bid_volume,
                    "ask_volume": ask_volume,
                    "imbalance_strength": bid_ratio - 0.5,
                }
            elif ask_ratio > threshold:
                return {
                    "tipo": "ask_dominance",
                    "bid_ratio": bid_ratio,
                    "ask_ratio": ask_ratio,
                    "bid_volume": bid_volume,
                    "ask_volume": ask_volume,
                    "imbalance_strength": ask_ratio - 0.5,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar orderbook imbalance: {e}")
            return None

    async def _executar_scalping_orderbook(
        self, symbol: str, imbalance: Dict, caso_uso: int
    ):
        """Executa scalping baseado em desequilíbrio do orderbook"""
        try:
            amount = 0.002
            tipo = imbalance["tipo"]

            self.logger.info(
                f"Desequilíbrio orderbook {symbol}: "
                f"{tipo} - Força: {imbalance['imbalance_strength']:.3f}"
            )

            if tipo == "bid_dominance":
                side = "buy"
            else:
                side = "sell"

            trade = await self.executar_trade(symbol, side, amount, caso_uso=caso_uso)

            if trade:
                self.posicoes_scalping[trade.id] = {
                    "tipo": "orderbook",
                    "entrada_time": datetime.now(),
                    "max_hold_time": 30,  # 30 segundos máximo
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "imbalance_original": imbalance,
                }

        except Exception as e:
            self.logger.error(f"Erro ao executar scalping orderbook: {e}")

    async def _gerenciar_posicoes_scalping(self):
        """Gerencia posições abertas de scalping"""
        agora = datetime.now()
        posicoes_para_fechar = []

        for trade_id, posicao in self.posicoes_scalping.items():
            tempo_aberto = (agora - posicao["entrada_time"]).total_seconds()

            if tempo_aberto >= posicao["max_hold_time"]:
                posicoes_para_fechar.append(trade_id)
                continue

            if "target_price" in posicao:
                ticker = await self.exchange_manager.get_ticker(posicao["symbol"])
                if ticker:
                    preco_atual = ticker["last"]

                    if (
                        posicao["side"] == "buy"
                        and preco_atual >= posicao["target_price"]
                    ):
                        posicoes_para_fechar.append(trade_id)
                    elif (
                        posicao["side"] == "sell"
                        and preco_atual <= posicao["target_price"]
                    ):
                        posicoes_para_fechar.append(trade_id)

        for trade_id in posicoes_para_fechar:
            await self._fechar_posicao_scalping(trade_id)

    async def _fechar_posicao_scalping(self, trade_id: str):
        """Fecha posição de scalping"""
        if trade_id not in self.posicoes_scalping:
            return

        posicao = self.posicoes_scalping[trade_id]

        side_fechamento = "sell" if posicao["side"] == "buy" else "buy"

        trade_fechamento = await self.executar_trade(
            posicao["symbol"],
            side_fechamento,
            posicao["amount"],
            caso_uso=posicao.get("caso_uso", 1),
        )

        if trade_fechamento:
            self.logger.info(f"Posição scalping fechada: {trade_id}")

        del self.posicoes_scalping[trade_id]

    async def executar_casos_paralelos(
        self, semaphore: asyncio.Semaphore, batch_size: int
    ):
        """Executa casos de uso em paralelo com semáforo"""
        async with semaphore:
            tasks = []
            for caso_uso in [1, 2, 3]:
                task = asyncio.create_task(self.executar_caso_uso(caso_uso))
                tasks.append(task)

                if len(tasks) >= batch_size:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
