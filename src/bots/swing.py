"""
Bot de Swing Trading
Operações de médio prazo seguindo swings de mercado
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .bot_base import BotBase
from src.utils.kpis import GerenciadorKPIs
from src.models.trade import Trade

logger = logging.getLogger(__name__)


class BotSwing(BotBase):
    """Bot de Swing Trading"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.nome = "swing"
        self.posicoes_swing = {}
        self.niveis_suporte_resistencia = {}
        self.fibonacci_levels = {}

    def get_intervalo_execucao(self) -> int:
        """Intervalo de execução em segundos (30 minutos para swing)"""
        return 1800

    async def executar(self):
        """Executa análise de swing trading em todos os casos de uso"""
        self.logger.info("Executando análise de swing trading")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(5)  # Pequeno delay entre casos de uso
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._swing_suporte_resistencia(parametros)
        elif caso_uso == 2:
            await self._swing_candlestick_patterns(parametros)
        elif caso_uso == 3:
            await self._swing_fibonacci(parametros)
        else:
            self.logger.warning(f"Caso de uso {caso_uso} não implementado")

    async def _swing_suporte_resistencia(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Swing com suporte e resistência"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        levels = parametros.get("levels", 5)
        proximity_percent = parametros.get("proximity_percent", 2) / 100

        for symbol in symbols:
            try:
                niveis = await self._identificar_suporte_resistencia(symbol, levels)
                if niveis:
                    await self._verificar_proximidade_niveis(
                        symbol, niveis, proximity_percent
                    )
            except Exception as e:
                self.logger.error(
                    f"Erro no swing suporte/resistência para {symbol}: {e}"
                )

    async def _identificar_suporte_resistencia(
        self, symbol: str, levels: int
    ) -> Optional[Dict]:
        """Identifica níveis de suporte e resistência"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1h", 200)
            if len(ohlcv) < 100:
                return None

            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]

            pivot_highs = self._encontrar_pivots(highs, "high", 10)

            pivot_lows = self._encontrar_pivots(lows, "low", 10)

            resistencias = self._agrupar_niveis(pivot_highs, levels)
            suportes = self._agrupar_niveis(pivot_lows, levels)

            return {
                "symbol": symbol,
                "resistencias": resistencias,
                "suportes": suportes,
                "preco_atual": ohlcv[-1][4],
                "timestamp": datetime.now(),
            }

        except Exception as e:
            self.logger.error(f"Erro ao identificar suporte/resistência: {e}")
            return None

    def _encontrar_pivots(
        self, prices: List[float], tipo: str, window: int
    ) -> List[Dict]:
        """Encontra pontos de pivot"""
        pivots = []

        for i in range(window, len(prices) - window):
            if tipo == "high":
                if all(
                    prices[i] >= prices[j]
                    for j in range(i - window, i + window + 1)
                    if j != i
                ):
                    if prices[i] == max(prices[i - window : i + window + 1]):
                        pivots.append(
                            {
                                "index": i,
                                "price": prices[i],
                                "strength": self._calcular_forca_pivot(
                                    prices, i, window
                                ),
                            }
                        )
            else:  # low
                if all(
                    prices[i] <= prices[j]
                    for j in range(i - window, i + window + 1)
                    if j != i
                ):
                    if prices[i] == min(prices[i - window : i + window + 1]):
                        pivots.append(
                            {
                                "index": i,
                                "price": prices[i],
                                "strength": self._calcular_forca_pivot(
                                    prices, i, window
                                ),
                            }
                        )

        pivots.sort(key=lambda x: x["strength"], reverse=True)
        return pivots[:10]  # Top 10 pivots

    def _calcular_forca_pivot(
        self, prices: List[float], index: int, window: int
    ) -> float:
        """Calcula força do pivot baseada na diferença com vizinhos"""
        pivot_price = prices[index]
        neighbors = (
            prices[max(0, index - window) : index]
            + prices[index + 1 : min(len(prices), index + window + 1)]
        )

        if not neighbors:
            return 0

        avg_neighbor = sum(neighbors) / len(neighbors)
        return abs(pivot_price - avg_neighbor) / avg_neighbor

    def _agrupar_niveis(self, pivots: List[Dict], max_levels: int) -> List[Dict]:
        """Agrupa pivots próximos em níveis"""
        if not pivots:
            return []

        niveis: List[Dict[str, Any]] = []
        tolerance = 0.02  # 2% de tolerância para agrupar

        for pivot in pivots:
            agrupado = False
            for nivel in niveis:
                if abs(pivot["price"] - nivel["price"]) / nivel["price"] <= tolerance:
                    total_strength = nivel["strength"] + pivot["strength"]
                    nivel["price"] = (
                        nivel["price"] * nivel["strength"]
                        + pivot["price"] * pivot["strength"]
                    ) / total_strength
                    nivel["strength"] = total_strength
                    nivel["touches"] += 1
                    agrupado = True
                    break

            if not agrupado and len(niveis) < max_levels:
                niveis.append(
                    {
                        "price": pivot["price"],
                        "strength": pivot["strength"],
                        "touches": 1,
                    }
                )

        niveis.sort(key=lambda x: x["strength"], reverse=True)
        return niveis[:max_levels]

    async def _verificar_proximidade_niveis(
        self, symbol: str, niveis: Dict, proximity_percent: float
    ):
        """Verifica proximidade do preço atual aos níveis"""
        preco_atual = niveis["preco_atual"]

        for resistencia in niveis["resistencias"]:
            distancia = abs(preco_atual - resistencia["price"]) / preco_atual
            if distancia <= proximity_percent:
                if preco_atual < resistencia["price"]:
                    sinal = {
                        "tipo": "swing_resistencia_rejeicao",
                        "symbol": symbol,
                        "nivel_resistencia": resistencia["price"],
                        "preco_atual": preco_atual,
                        "forca_nivel": resistencia["strength"],
                        "target_suporte": min(
                            [s["price"] for s in niveis["suportes"]],
                            default=preco_atual * 0.95,
                        ),
                    }
                    await self._executar_swing_trade(symbol, sinal, 1)

        for suporte in niveis["suportes"]:
            distancia = abs(preco_atual - suporte["price"]) / preco_atual
            if distancia <= proximity_percent:
                if preco_atual > suporte["price"]:
                    sinal = {
                        "tipo": "swing_suporte_bounce",
                        "symbol": symbol,
                        "nivel_suporte": suporte["price"],
                        "preco_atual": preco_atual,
                        "forca_nivel": suporte["strength"],
                        "target_resistencia": max(
                            [r["price"] for r in niveis["resistencias"]],
                            default=preco_atual * 1.05,
                        ),
                    }
                    await self._executar_swing_trade(symbol, sinal, 1)

    async def _swing_candlestick_patterns(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Swing com padrões de candlestick"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        patterns = parametros.get("patterns", ["doji", "hammer", "engulfing"])

        for symbol in symbols:
            try:
                pattern_signal = await self._detectar_candlestick_patterns(
                    symbol, patterns
                )
                if pattern_signal:
                    await self._executar_swing_trade(symbol, pattern_signal, 2)
            except Exception as e:
                self.logger.error(f"Erro no swing candlestick para {symbol}: {e}")

    async def _detectar_candlestick_patterns(
        self, symbol: str, patterns: List[str]
    ) -> Optional[Dict]:
        """Detecta padrões de candlestick"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1h", 50)
            if len(ohlcv) < 10:
                return None

            candles = ohlcv[-5:]

            for pattern in patterns:
                if pattern == "doji":
                    doji = self._detectar_doji(candles[-1])
                    if doji:
                        return {
                            "tipo": "swing_doji",
                            "pattern": "doji",
                            "candle": candles[-1],
                            "forca": doji["forca"],
                            "direcao_sugerida": doji["direcao"],
                        }

                elif pattern == "hammer":
                    hammer = self._detectar_hammer(candles[-1])
                    if hammer:
                        return {
                            "tipo": "swing_hammer",
                            "pattern": "hammer",
                            "candle": candles[-1],
                            "forca": hammer["forca"],
                            "direcao_sugerida": "alta",
                        }

                elif pattern == "engulfing":
                    engulfing = self._detectar_engulfing(candles[-2:])
                    if engulfing:
                        return {
                            "tipo": "swing_engulfing",
                            "pattern": "engulfing",
                            "candles": candles[-2:],
                            "forca": engulfing["forca"],
                            "direcao_sugerida": engulfing["direcao"],
                        }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar candlestick patterns: {e}")
            return None

    def _detectar_doji(self, candle: List) -> Optional[Dict]:
        """Detecta padrão Doji"""
        open_price = candle[1]
        high = candle[2]
        low = candle[3]
        close = candle[4]

        body = abs(close - open_price)
        total_range = high - low

        if total_range == 0:
            return None

        body_percent = body / total_range

        if body_percent < 0.1:
            upper_shadow = high - max(open_price, close)
            lower_shadow = min(open_price, close) - low

            if upper_shadow > lower_shadow * 2:
                direcao = "baixa"  # Gravestone doji
            elif lower_shadow > upper_shadow * 2:
                direcao = "alta"  # Dragonfly doji
            else:
                direcao = "neutro"  # Doji clássico

            return {
                "forca": 1 - body_percent,
                "direcao": direcao,
                "upper_shadow": upper_shadow,
                "lower_shadow": lower_shadow,
            }

        return None

    def _detectar_hammer(self, candle: List) -> Optional[Dict]:
        """Detecta padrão Hammer"""
        open_price = candle[1]
        high = candle[2]
        low = candle[3]
        close = candle[4]

        body = abs(close - open_price)
        total_range = high - low

        if total_range == 0:
            return None

        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)

        if (
            lower_shadow > body * 2
            and upper_shadow < body * 0.5
            and body / total_range < 0.3
        ):

            return {
                "forca": lower_shadow / total_range,
                "body_size": body / total_range,
                "shadow_ratio": lower_shadow / upper_shadow if upper_shadow > 0 else 10,
            }

        return None

    def _detectar_engulfing(self, candles: List[List]) -> Optional[Dict]:
        """Detecta padrão Engulfing"""
        if len(candles) < 2:
            return None

        candle1 = candles[0]  # Candle anterior
        candle2 = candles[1]  # Candle atual

        open1, close1 = candle1[1], candle1[4]
        open2, close2 = candle2[1], candle2[4]

        if (
            close1 < open1  # Candle anterior bearish
            and close2 > open2  # Candle atual bullish
            and open2 < close1  # Abre abaixo do fechamento anterior
            and close2 > open1
        ):  # Fecha acima da abertura anterior

            engulfing_size = (close2 - open2) / (open1 - close1)
            return {
                "direcao": "alta",
                "forca": min(2.0, engulfing_size),
                "tipo": "bullish_engulfing",
            }

        elif (
            close1 > open1  # Candle anterior bullish
            and close2 < open2  # Candle atual bearish
            and open2 > close1  # Abre acima do fechamento anterior
            and close2 < open1
        ):  # Fecha abaixo da abertura anterior

            engulfing_size = (open2 - close2) / (close1 - open1)
            return {
                "direcao": "baixa",
                "forca": min(2.0, engulfing_size),
                "tipo": "bearish_engulfing",
            }

        return None

    async def _swing_fibonacci(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Swing com análise de fibonacci"""
        symbols = ["BTC/USDT", "ETH/USDT"]
        retracement_levels = parametros.get("retracement_levels", [0.382, 0.618])

        for symbol in symbols:
            try:
                fib_analysis = await self._analisar_fibonacci(
                    symbol, retracement_levels
                )
                if fib_analysis:
                    await self._executar_swing_trade(symbol, fib_analysis, 3)
            except Exception as e:
                self.logger.error(f"Erro no swing fibonacci para {symbol}: {e}")

    async def _analisar_fibonacci(
        self, symbol: str, levels: List[float]
    ) -> Optional[Dict]:
        """Analisa níveis de retração de Fibonacci"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1h", 100)
            if len(ohlcv) < 50:
                return None

            highs = [candle[2] for candle in ohlcv]
            lows = [candle[3] for candle in ohlcv]
            closes = [candle[4] for candle in ohlcv]

            swing_high = max(highs[-50:])
            swing_low = min(lows[-50:])
            preco_atual = closes[-1]

            fib_range = swing_high - swing_low
            fib_levels = {}

            for level in levels:
                fib_levels[f"ret_{level}"] = swing_high - (fib_range * level)
                fib_levels[f"ext_{level}"] = swing_high + (fib_range * level)

            for level_name, level_price in fib_levels.items():
                distancia_percent = abs(preco_atual - level_price) / preco_atual

                if distancia_percent <= 0.015:  # Dentro de 1.5% do nível
                    if "ret_" in level_name:
                        if preco_atual < level_price:
                            direcao = "alta"  # Bounce do suporte Fibonacci
                        else:
                            direcao = "baixa"  # Rejeição da resistência Fibonacci
                    else:  # extensão
                        direcao = "alta" if "0.618" in level_name else "baixa"

                    return {
                        "tipo": f"swing_fibonacci_{direcao}",
                        "nivel_fib": level_name,
                        "preco_nivel": level_price,
                        "preco_atual": preco_atual,
                        "distancia_percent": distancia_percent,
                        "swing_high": swing_high,
                        "swing_low": swing_low,
                        "fib_range": fib_range,
                        "direcao": direcao,
                    }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao analisar fibonacci: {e}")
            return None

    async def _executar_swing_trade(self, symbol: str, sinal: Dict, caso_uso: int):
        """Executa trade de swing"""
        try:
            tipo = sinal["tipo"]
            amount = 0.02  # Quantidade maior para swing trading

            if "alta" in tipo or "compra" in tipo:
                side = "buy"
                self.logger.info(f"Swing ALTA para {symbol}: {tipo}")
            elif "baixa" in tipo or "venda" in tipo:
                side = "sell"
                self.logger.info(f"Swing BAIXA para {symbol}: {tipo}")
            else:
                return

            trade = await self.executar_trade(symbol, side, amount, caso_uso=caso_uso)

            if trade:
                await self._definir_targets_swing(trade, sinal)

                self.posicoes_swing[trade.id] = {
                    "sinal": sinal,
                    "timestamp": datetime.now(),
                    "symbol": symbol,
                    "side": side,
                    "caso_uso": caso_uso,
                }

        except Exception as e:
            self.logger.error(f"Erro ao executar swing trade: {e}")

    async def _definir_targets_swing(self, trade, sinal: Dict):
        """Define targets para swing trading"""
        try:
            tipo = sinal["tipo"]

            if "suporte" in tipo or "resistencia" in tipo:
                if "target_resistencia" in sinal:
                    target_price = sinal["target_resistencia"]
                elif "target_suporte" in sinal:
                    target_price = sinal["target_suporte"]
                else:
                    target_price = trade.price * (1.08 if trade.side == "buy" else 0.92)

                stop_percent = 0.04  # 4% stop para swing

            elif "candlestick" in tipo:
                target_percent = 0.06  # 6% target
                target_price = trade.price * (
                    1 + target_percent if trade.side == "buy" else 1 - target_percent
                )
                stop_percent = 0.03  # 3% stop

            elif "fibonacci" in tipo:
                if "swing_high" in sinal and "swing_low" in sinal:
                    fib_range = sinal["swing_high"] - sinal["swing_low"]
                    if trade.side == "buy":
                        target_price = trade.price + (fib_range * 0.618)
                    else:
                        target_price = trade.price - (fib_range * 0.618)
                else:
                    target_price = trade.price * (1.1 if trade.side == "buy" else 0.9)

                stop_percent = 0.05  # 5% stop

            else:
                target_price = trade.price * (1.08 if trade.side == "buy" else 0.92)
                stop_percent = 0.04

            if trade.side == "buy":
                stop_price = trade.price * (1 - stop_percent)
            else:
                stop_price = trade.price * (1 + stop_percent)

            self.logger.info(
                f"Targets swing definidos para {trade.symbol}: "
                f"Target: {target_price:.4f}, Stop: {stop_price:.4f}"
            )

        except Exception as e:
            self.logger.error(f"Erro ao definir targets swing: {e}")

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
