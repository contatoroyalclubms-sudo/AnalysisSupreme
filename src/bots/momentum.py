"""
Bot Momentum - Segue tendências de alta/baixa do mercado
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .bot_base import BotBase
from ..utils.kpis import GerenciadorKPIs


class BotMomentum(BotBase):
    """Bot especializado em momentum trading"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.sinais_momentum = {}
        self.posicoes_momentum = {}

    def get_intervalo_execucao(self) -> int:
        """Intervalo de 120 segundos para momentum"""
        return 120

    async def executar(self):
        """Executa momentum trading em todos os casos de uso"""
        self.logger.info("Executando momentum trading")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(15)
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico de momentum"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._momentum_breakout(parametros)
        elif caso_uso == 2:
            await self._momentum_continuacao(parametros)
        elif caso_uso == 3:
            await self._momentum_volume(parametros)

    async def _momentum_breakout(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Momentum de breakout"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        volume_confirm = parametros.get("volume_confirm", False)

        for symbol in symbols:
            try:
                breakout = await self._detectar_breakout(symbol, volume_confirm)
                if breakout:
                    await self._executar_momentum_trade(symbol, breakout, 1)
            except Exception as e:
                self.logger.error(f"Erro no momentum breakout para {symbol}: {e}")

    async def _detectar_breakout(self, symbol: str, volume_confirm: bool) -> Optional[Dict]:
        """Detecta breakout de resistência/suporte"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "5m", 100)
            if len(ohlcv) < 50:
                return None

            highs = [candle[2] for candle in ohlcv[-50:]]
            lows = [candle[3] for candle in ohlcv[-50:]]
            closes = [candle[4] for candle in ohlcv[-50:]]
            volumes = [candle[5] for candle in ohlcv[-50:]]

            resistencia = max(highs[-20:])
            suporte = min(lows[-20:])
            preco_atual = closes[-1]
            volume_atual = volumes[-1]
            volume_medio = sum(volumes[-20:]) / 20

            if preco_atual > resistencia * 1.002:  # 0.2% acima da resistência
                if not volume_confirm or volume_atual > volume_medio * 1.5:
                    return {
                        "tipo": "breakout_alta",
                        "preco_breakout": resistencia,
                        "preco_atual": preco_atual,
                        "volume_ratio": volume_atual / volume_medio,
                        "forca": (preco_atual - resistencia) / resistencia,
                    }

            elif preco_atual < suporte * 0.998:  # 0.2% abaixo do suporte
                if not volume_confirm or volume_atual > volume_medio * 1.5:
                    return {
                        "tipo": "breakout_baixa",
                        "preco_breakout": suporte,
                        "preco_atual": preco_atual,
                        "volume_ratio": volume_atual / volume_medio,
                        "forca": (suporte - preco_atual) / suporte,
                    }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar breakout: {e}")
            return None

    async def _momentum_continuacao(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Momentum de continuação de tendência"""
        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
        trend_confirm = parametros.get("trend_confirm", True)

        for symbol in symbols:
            try:
                continuacao = await self._detectar_continuacao_tendencia(symbol, trend_confirm)
                if continuacao:
                    await self._executar_momentum_trade(symbol, continuacao, 2)
            except Exception as e:
                self.logger.error(f"Erro no momentum continuação para {symbol}: {e}")

    async def _detectar_continuacao_tendencia(self, symbol: str, trend_confirm: bool) -> Optional[Dict]:
        """Detecta continuação de tendência"""
        try:
            analise = await self.analisar_mercado(symbol)
            if not analise or not analise.get("analise_tecnica"):
                return None

            tecnica = analise["analise_tecnica"]

            if tecnica["sma_20"] > tecnica["sma_50"]:
                if tecnica["preco_atual"] > tecnica["sma_20"] * 1.01:
                    momentum_score = self._calcular_momentum_score(analise)

                    if momentum_score > 0.6:
                        return {
                            "tipo": "continuacao_alta",
                            "tendencia": "alta",
                            "momentum_score": momentum_score,
                            "preco_entrada": tecnica["preco_atual"],
                            "sma_20": tecnica["sma_20"],
                        }

            elif tecnica["sma_20"] < tecnica["sma_50"]:
                if tecnica["preco_atual"] < tecnica["sma_20"] * 0.99:
                    momentum_score = self._calcular_momentum_score(analise)

                    if momentum_score > 0.6:
                        return {
                            "tipo": "continuacao_baixa",
                            "tendencia": "baixa",
                            "momentum_score": momentum_score,
                            "preco_entrada": tecnica["preco_atual"],
                            "sma_20": tecnica["sma_20"],
                        }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar continuação: {e}")
            return None

    async def _momentum_volume(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Momentum com confirmação de volume"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        volume_threshold = parametros.get("volume_threshold", 1.5)

        for symbol in symbols:
            try:
                momentum_volume = await self._detectar_momentum_volume(symbol, volume_threshold)
                if momentum_volume:
                    await self._executar_momentum_trade(symbol, momentum_volume, 3)
            except Exception as e:
                self.logger.error(f"Erro no momentum volume para {symbol}: {e}")

    async def _detectar_momentum_volume(self, symbol: str, volume_threshold: float) -> Optional[Dict]:
        """Detecta momentum com confirmação de volume"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1m", 30)
            if len(ohlcv) < 20:
                return None

            closes = [candle[4] for candle in ohlcv]
            volumes = [candle[5] for candle in ohlcv]

            preco_momentum = (closes[-1] - closes[-10]) / closes[-10]

            volume_atual = volumes[-1]
            volume_medio = sum(volumes[-10:]) / 10
            volume_ratio = volume_atual / volume_medio

            if abs(preco_momentum) > 0.005 and volume_ratio > volume_threshold:
                direcao = "alta" if preco_momentum > 0 else "baixa"

                return {
                    "tipo": f"momentum_volume_{direcao}",
                    "preco_momentum": preco_momentum,
                    "volume_ratio": volume_ratio,
                    "forca_sinal": abs(preco_momentum) * volume_ratio,
                    "direcao": direcao,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar momentum volume: {e}")
            return None

    def _calcular_momentum_score(self, analise: Dict) -> float:
        """Calcula score de momentum (0-1)"""
        try:
            tecnica = analise["analise_tecnica"]
            ia = analise.get("analise_ia", {})

            score = 0.0

            if tecnica["sma_20"] > tecnica["sma_50"]:
                score += 0.3

            rsi = tecnica.get("rsi", 50)
            if 30 < rsi < 70:  # RSI neutro é bom para momentum
                score += 0.2

            volume_ratio = tecnica.get("volume_ratio", 1)
            if volume_ratio > 1.2:
                score += 0.2

            if ia.get("predicao_direcao") == tecnica.get("tendencia"):
                score += 0.3

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"Erro ao calcular momentum score: {e}")
            return 0.0

    async def _executar_momentum_trade(self, symbol: str, sinal: Dict, caso_uso: int):
        """Executa trade baseado em sinal de momentum"""
        try:
            tipo = sinal["tipo"]
            amount = 0.01  # Quantidade fixa

            if "alta" in tipo or "breakout_alta" in tipo:
                side = "buy"
                self.logger.info(f"Sinal de momentum ALTA para {symbol}: {tipo}")
            elif "baixa" in tipo or "breakout_baixa" in tipo:
                side = "sell"
                self.logger.info(f"Sinal de momentum BAIXA para {symbol}: {tipo}")
            else:
                return

            trade = await self.executar_trade(symbol, side, amount, caso_uso=caso_uso)

            if trade:
                self.sinais_momentum[trade.id] = {"sinal": sinal, "timestamp": datetime.now(), "symbol": symbol, "side": side}

                await self._definir_stop_take_profit(trade, sinal)

        except Exception as e:
            self.logger.error(f"Erro ao executar momentum trade: {e}")

    async def _definir_stop_take_profit(self, trade, sinal: Dict):
        """Define stop loss e take profit para trade de momentum"""
        try:
            if "breakout" in sinal["tipo"]:
                stop_percent = 0.02  # 2% stop loss
                take_profit_percent = 0.06  # 6% take profit
            elif "continuacao" in sinal["tipo"]:
                stop_percent = 0.015  # 1.5% stop loss
                take_profit_percent = 0.045  # 4.5% take profit
            else:
                stop_percent = 0.01  # 1% stop loss
                take_profit_percent = 0.03  # 3% take profit

            if trade.side == "buy":
                stop_price = trade.price * (1 - stop_percent)
                take_profit_price = trade.price * (1 + take_profit_percent)
            else:
                stop_price = trade.price * (1 + stop_percent)
                take_profit_price = trade.price * (1 - take_profit_percent)

            self.posicoes_momentum[trade.id] = {
                "stop_loss": stop_price,
                "take_profit": take_profit_price,
                "entrada": trade.price,
                "timestamp": datetime.now(),
            }

            self.logger.info(f"Stop/TP definidos para {trade.symbol}: " f"Stop: {stop_price:.4f}, TP: {take_profit_price:.4f}")

        except Exception as e:
            self.logger.error(f"Erro ao definir stop/take profit: {e}")

    async def executar_casos_paralelos(self, semaphore: asyncio.Semaphore, batch_size: int):
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
