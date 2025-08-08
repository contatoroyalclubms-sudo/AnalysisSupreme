"""
Bot Mean Reversion - Retorno à média de preços
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import math

from .bot_base import BotBase
from ..utils.kpis import GerenciadorKPIs


class BotMeanReversion(BotBase):
    """Bot especializado em mean reversion"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.medias_historicas = {}
        self.posicoes_reversion = {}

    def get_intervalo_execucao(self) -> int:
        """Intervalo de 180 segundos para mean reversion"""
        return 180

    async def executar(self):
        """Executa mean reversion em todos os casos de uso"""
        self.logger.info("Executando mean reversion")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(20)
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico de mean reversion"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._mean_reversion_simples(parametros)
        elif caso_uso == 2:
            await self._mean_reversion_bollinger(parametros)
        elif caso_uso == 3:
            await self._mean_reversion_rsi_divergence(parametros)

    async def _mean_reversion_simples(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Reversão à média simples"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        media_type = parametros.get("media_type", "sma")
        lookback = parametros.get("lookback_period", 50)

        for symbol in symbols:
            try:
                reversion = await self._detectar_reversion_simples(
                    symbol, media_type, lookback
                )
                if reversion:
                    await self._executar_mean_reversion_trade(symbol, reversion, 1)
            except Exception as e:
                self.logger.error(f"Erro na mean reversion simples para {symbol}: {e}")

    async def _detectar_reversion_simples(
        self, symbol: str, media_type: str, lookback: int
    ) -> Optional[Dict]:
        """Detecta oportunidade de reversão à média simples"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "15m", lookback + 10)
            if len(ohlcv) < lookback:
                return None

            closes = [candle[4] for candle in ohlcv]
            preco_atual = closes[-1]

            if media_type == "sma":
                media = sum(closes[-lookback:]) / lookback
            else:  # EMA
                media = self._calcular_ema(closes[-lookback:])

            desvio_percent = (preco_atual - media) / media

            returns = [
                (closes[i] - closes[i - 1]) / closes[i - 1]
                for i in range(1, len(closes))
            ]
            volatilidade = self._calcular_volatilidade(returns[-lookback:])

            threshold = volatilidade * 2

            if abs(desvio_percent) > threshold:
                direcao = "baixa" if desvio_percent > 0 else "alta"  # Reverter

                return {
                    "tipo": f"reversion_{direcao}",
                    "media": media,
                    "preco_atual": preco_atual,
                    "desvio_percent": desvio_percent,
                    "volatilidade": volatilidade,
                    "threshold": threshold,
                    "forca_sinal": abs(desvio_percent) / threshold,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar reversão simples: {e}")
            return None

    def _calcular_ema(self, prices: List[float], alpha: float = 0.1) -> float:
        """Calcula EMA (Exponential Moving Average)"""
        if not prices:
            return 0.0

        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema

        return ema

    def _calcular_volatilidade(self, returns: List[float]) -> float:
        """Calcula volatilidade dos retornos"""
        if len(returns) < 2:
            return 0.02  # Volatilidade padrão

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)

        return math.sqrt(variance)

    async def _mean_reversion_bollinger(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Reversão com bandas de Bollinger"""
        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
        std_dev = parametros.get("std_dev", 2)
        period = parametros.get("lookback_period", 20)

        for symbol in symbols:
            try:
                bollinger = await self._detectar_bollinger_reversion(
                    symbol, period, std_dev
                )
                if bollinger:
                    await self._executar_mean_reversion_trade(symbol, bollinger, 2)
            except Exception as e:
                self.logger.error(f"Erro na Bollinger reversion para {symbol}: {e}")

    async def _detectar_bollinger_reversion(
        self, symbol: str, period: int, std_dev: float
    ) -> Optional[Dict]:
        """Detecta reversão usando Bandas de Bollinger"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "30m", period + 10)
            if len(ohlcv) < period:
                return None

            closes = [candle[4] for candle in ohlcv[-period:]]
            preco_atual = closes[-1]

            sma = sum(closes) / len(closes)
            variance = sum((price - sma) ** 2 for price in closes) / len(closes)
            std = math.sqrt(variance)

            banda_superior = sma + (std_dev * std)
            banda_inferior = sma - (std_dev * std)

            if preco_atual >= banda_superior:
                return {
                    "tipo": "bollinger_reversion_baixa",
                    "sma": sma,
                    "banda_superior": banda_superior,
                    "banda_inferior": banda_inferior,
                    "preco_atual": preco_atual,
                    "distancia_banda": (preco_atual - banda_superior) / banda_superior,
                    "std_dev": std,
                }
            elif preco_atual <= banda_inferior:
                return {
                    "tipo": "bollinger_reversion_alta",
                    "sma": sma,
                    "banda_superior": banda_superior,
                    "banda_inferior": banda_inferior,
                    "preco_atual": preco_atual,
                    "distancia_banda": (banda_inferior - preco_atual) / banda_inferior,
                    "std_dev": std,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar Bollinger reversion: {e}")
            return None

    async def _mean_reversion_rsi_divergence(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Reversão com RSI divergente"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        rsi_period = parametros.get("rsi_period", 14)

        for symbol in symbols:
            try:
                divergence = await self._detectar_rsi_divergence(symbol, rsi_period)
                if divergence:
                    await self._executar_mean_reversion_trade(symbol, divergence, 3)
            except Exception as e:
                self.logger.error(f"Erro na RSI divergence para {symbol}: {e}")

    async def _detectar_rsi_divergence(
        self, symbol: str, rsi_period: int
    ) -> Optional[Dict]:
        """Detecta divergência no RSI"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1h", rsi_period + 20)
            if len(ohlcv) < rsi_period + 10:
                return None

            closes = [candle[4] for candle in ohlcv]
            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]

            rsi_values = self._calcular_rsi_series(closes, rsi_period)
            if len(rsi_values) < 10:
                return None

            preco_low_atual = min(lows[-5:])
            preco_low_anterior = min(lows[-15:-10])
            rsi_low_atual = min(rsi_values[-5:])
            rsi_low_anterior = min(rsi_values[-15:-10])

            if (
                preco_low_atual < preco_low_anterior
                and rsi_low_atual > rsi_low_anterior
                and rsi_low_atual < 40
            ):

                return {
                    "tipo": "rsi_divergence_bullish",
                    "preco_atual": closes[-1],
                    "rsi_atual": rsi_values[-1],
                    "preco_low_atual": preco_low_atual,
                    "preco_low_anterior": preco_low_anterior,
                    "rsi_low_atual": rsi_low_atual,
                    "rsi_low_anterior": rsi_low_anterior,
                    "forca_divergencia": rsi_low_anterior - rsi_low_atual,
                }

            preco_high_atual = max(highs[-5:])
            preco_high_anterior = max(highs[-15:-10])
            rsi_high_atual = max(rsi_values[-5:])
            rsi_high_anterior = max(rsi_values[-15:-10])

            if (
                preco_high_atual > preco_high_anterior
                and rsi_high_atual < rsi_high_anterior
                and rsi_high_atual > 60
            ):

                return {
                    "tipo": "rsi_divergence_bearish",
                    "preco_atual": closes[-1],
                    "rsi_atual": rsi_values[-1],
                    "preco_high_atual": preco_high_atual,
                    "preco_high_anterior": preco_high_anterior,
                    "rsi_high_atual": rsi_high_atual,
                    "rsi_high_anterior": rsi_high_anterior,
                    "forca_divergencia": rsi_high_anterior - rsi_high_atual,
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar RSI divergence: {e}")
            return None

    def _calcular_rsi_series(self, closes: List[float], period: int) -> List[float]:
        """Calcula série de valores RSI"""
        if len(closes) < period + 1:
            return []

        rsi_values = []

        for i in range(period, len(closes)):
            window = closes[i - period : i + 1]
            deltas = [window[j] - window[j - 1] for j in range(1, len(window))]

            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]

            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return rsi_values

    async def _executar_mean_reversion_trade(
        self, symbol: str, sinal: Dict, caso_uso: int
    ):
        """Executa trade de mean reversion"""
        try:
            tipo = sinal["tipo"]
            amount = 0.01

            if "alta" in tipo or "bullish" in tipo:
                side = "buy"
                self.logger.info(f"Mean reversion ALTA para {symbol}: {tipo}")
            elif "baixa" in tipo or "bearish" in tipo:
                side = "sell"
                self.logger.info(f"Mean reversion BAIXA para {symbol}: {tipo}")
            else:
                return

            trade = await self.executar_trade(symbol, side, amount, caso_uso=caso_uso)

            if trade:
                await self._definir_targets_reversion(trade, sinal)

        except Exception as e:
            self.logger.error(f"Erro ao executar mean reversion trade: {e}")

    async def _definir_targets_reversion(self, trade, sinal: Dict):
        """Define targets para trade de mean reversion"""
        try:
            tipo = sinal["tipo"]

            if "simples" in tipo:
                if "media" in sinal:
                    target_price = sinal["media"]
                else:
                    target_price = trade.price * (1.02 if trade.side == "buy" else 0.98)

                stop_percent = 0.015  # 1.5% stop

            elif "bollinger" in tipo:
                target_price = sinal["sma"]
                stop_percent = 0.02  # 2% stop

            elif "rsi_divergence" in tipo:
                target_percent = min(0.05, sinal.get("forca_divergencia", 10) / 1000)
                target_price = trade.price * (
                    1 + target_percent if trade.side == "buy" else 1 - target_percent
                )
                stop_percent = 0.025  # 2.5% stop

            else:
                target_price = trade.price * (1.03 if trade.side == "buy" else 0.97)
                stop_percent = 0.02

            if trade.side == "buy":
                stop_price = trade.price * (1 - stop_percent)
            else:
                stop_price = trade.price * (1 + stop_percent)

            self.posicoes_reversion[trade.id] = {
                "target_price": target_price,
                "stop_price": stop_price,
                "entrada": trade.price,
                "tipo_reversion": tipo,
                "timestamp": datetime.now(),
            }

            self.logger.info(
                f"Targets definidos para {trade.symbol}: "
                f"Target: {target_price:.4f}, Stop: {stop_price:.4f}"
            )

        except Exception as e:
            self.logger.error(f"Erro ao definir targets reversion: {e}")

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
