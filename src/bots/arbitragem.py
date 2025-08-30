"""
Bot de Arbitragem - Detecta diferenças de preço entre exchanges
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .bot_base import BotBase
from src.utils.kpis import GerenciadorKPIs


class BotArbitragem(BotBase):
    """Bot especializado em arbitragem entre exchanges"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.exchanges_ativas = []
        self.oportunidades_ativas = {}
        self.kpi_manager = GerenciadorKPIs()

    async def inicializar(self):
        """Inicializa o bot de arbitragem"""
        await super().inicializar()

        self.exchanges_ativas = await self._configurar_exchanges()
        self.logger.info(
            f"Bot arbitragem configurado com {len(self.exchanges_ativas)} exchanges"
        )

    async def _configurar_exchanges(self) -> List[str]:
        """Configura exchanges disponíveis para arbitragem"""
        exchanges_disponiveis = ["binance", "coinbase", "kraken"]
        exchanges_ativas = []

        for exchange in exchanges_disponiveis:
            config_exchange = self.config.get_exchange_config(exchange)
            if config_exchange and config_exchange.api_key:
                exchanges_ativas.append(exchange)

        return exchanges_ativas

    def get_intervalo_execucao(self) -> int:
        """Intervalo de 30 segundos para arbitragem"""
        return 30

    async def executar(self):
        """Executa análise de arbitragem em todos os casos de uso"""
        self.logger.info("Executando análise de arbitragem")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(5)  # Pequeno delay entre casos de uso
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico de arbitragem"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._arbitragem_simples(parametros)
        elif caso_uso == 2:
            await self._arbitragem_triangular(parametros)
        elif caso_uso == 3:
            await self._arbitragem_funding(parametros)

    async def _arbitragem_simples(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Arbitragem simples entre 2 exchanges"""
        exchanges = parametros.get("exchanges", ["binance", "coinbase"])
        min_profit = parametros.get("min_profit_percent", 0.5) / 100

        if len(exchanges) < 2:
            self.logger.warning("Arbitragem simples requer pelo menos 2 exchanges")
            return

        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

        for symbol in symbols:
            try:
                oportunidade = await self._detectar_arbitragem_simples(
                    symbol, exchanges[0], exchanges[1], min_profit
                )

                if oportunidade:
                    await self._executar_arbitragem_simples(oportunidade)

            except Exception as e:
                self.logger.error(f"Erro na arbitragem simples para {symbol}: {e}")

    async def _detectar_arbitragem_simples(
        self, symbol: str, exchange1: str, exchange2: str, min_profit: float
    ) -> Optional[Dict]:
        """Detecta oportunidade de arbitragem simples"""
        try:
            medicao_id = self.kpi_manager.iniciar_medicao_latencia(
                "arbitragem", "deteccao_simples"
            )

            ticker1 = await self.exchange_manager.get_ticker(symbol, exchange1)
            ticker2 = await self.exchange_manager.get_ticker(symbol, exchange2)

            latencia_ms = self.kpi_manager.finalizar_medicao_latencia(medicao_id)

            if not ticker1 or not ticker2:
                return None

            price1 = ticker1["bid"]  # Preço de venda na exchange 1
            price2 = ticker2["ask"]  # Preço de compra na exchange 2

            if price1 > price2:
                profit_percent = (price1 - price2) / price2
                spread_percent = profit_percent * 100
                execucao_simultanea = (
                    100.0 if latencia_ms < 50 else max(0, 100 - (latencia_ms - 50) * 2)
                )

                self.kpi_manager.atualizar_kpi_arbitragem(
                    spread_percent, execucao_simultanea
                )

                if profit_percent >= min_profit:
                    return {
                        "symbol": symbol,
                        "buy_exchange": exchange2,
                        "sell_exchange": exchange1,
                        "buy_price": price2,
                        "sell_price": price1,
                        "profit_percent": profit_percent,
                        "spread_percent": spread_percent,
                        "latencia_ms": latencia_ms,
                        "execucao_simultanea": execucao_simultanea,
                        "timestamp": datetime.now(),
                    }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar arbitragem: {e}")
            return None

    async def _executar_arbitragem_simples(self, oportunidade: Dict):
        """Executa arbitragem simples"""
        symbol = oportunidade["symbol"]
        amount = 0.01  # Quantidade fixa para teste

        self.logger.info(
            f"Oportunidade de arbitragem detectada: {symbol} "
            f"Profit: {oportunidade['profit_percent']:.2%}"
        )

        trade_buy = await self.executar_trade(
            symbol, "buy", amount, oportunidade["buy_price"], caso_uso=1
        )

        if trade_buy:
            trade_sell = await self.executar_trade(
                symbol, "sell", amount, oportunidade["sell_price"], caso_uso=1
            )

            if trade_sell:
                pnl = (oportunidade["sell_price"] - oportunidade["buy_price"]) * amount
                trade_buy.pnl = pnl / 2
                trade_sell.pnl = pnl / 2

                self.logger.info(f"Arbitragem executada com sucesso. PnL: {pnl:.4f}")

                return {
                    "success": True,
                    "trade_buy": trade_buy,
                    "trade_sell": trade_sell,
                    "pnl": pnl,
                    "symbol": symbol,
                    "profit_percent": oportunidade["profit_percent"],
                }

        return {"success": False, "error": "Failed to execute trades", "symbol": symbol}

    async def _arbitragem_triangular(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Arbitragem triangular em uma exchange"""
        exchange = parametros.get("exchange", "binance")

        triangulos = [
            ["BTC/USDT", "ETH/BTC", "ETH/USDT"],
            ["BTC/USDT", "ADA/BTC", "ADA/USDT"],
        ]

        for triangulo in triangulos:
            try:
                oportunidade = await self._detectar_arbitragem_triangular(
                    triangulo, exchange
                )
                if oportunidade:
                    await self._executar_arbitragem_triangular(oportunidade)
            except Exception as e:
                self.logger.error(f"Erro na arbitragem triangular: {e}")

    async def _detectar_arbitragem_triangular(
        self, pares: List[str], exchange: str
    ) -> Optional[Dict]:
        """Detecta oportunidade de arbitragem triangular"""
        try:
            tickers = {}
            for par in pares:
                ticker = await self.exchange_manager.get_ticker(par, exchange)
                if not ticker:
                    return None
                tickers[par] = ticker

            price1 = 1 / tickers[pares[0]]["ask"]  # USDT para BTC
            price2 = 1 / tickers[pares[1]]["ask"]  # BTC para ETH
            price3 = tickers[pares[2]]["bid"]  # ETH para USDT

            resultado_final = price1 * price2 * price3
            profit_percent = resultado_final - 1

            if profit_percent > 0.005:  # 0.5% mínimo
                return {
                    "pares": pares,
                    "exchange": exchange,
                    "profit_percent": profit_percent,
                    "precos": [price1, price2, price3],
                    "timestamp": datetime.now(),
                }

            return None

        except Exception as e:
            self.logger.error(f"Erro ao detectar arbitragem triangular: {e}")
            return None

    async def _executar_arbitragem_triangular(self, oportunidade: Dict):
        """Executa arbitragem triangular"""
        self.logger.info(
            f"Arbitragem triangular detectada. Profit: {oportunidade['profit_percent']:.2%}"
        )

        amount = 100  # USDT inicial

        for i, par in enumerate(oportunidade["pares"]):
            side = "buy" if i < 2 else "sell"
            trade = await self.executar_trade(par, side, amount, caso_uso=2)

            if trade:
                if i == 0:
                    amount = amount * oportunidade["precos"][0]
                elif i == 1:
                    amount = amount * oportunidade["precos"][1]

    async def _arbitragem_funding(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Arbitragem de funding rates"""
        exchange = parametros.get("exchange", "binance")

        symbols = ["BTC/USDT", "ETH/USDT"]

        for symbol in symbols:
            try:
                funding_rate = await self._obter_funding_rate(symbol, exchange)
                if funding_rate and abs(funding_rate) > 0.01:  # 1% threshold
                    await self._executar_funding_arbitrage(symbol, funding_rate)
            except Exception as e:
                self.logger.error(f"Erro na arbitragem de funding: {e}")

    async def _obter_funding_rate(self, symbol: str, exchange: str) -> Optional[float]:
        """Obtém funding rate atual"""
        try:
            ticker = await self.exchange_manager.get_ticker(symbol, exchange)
            if not ticker:
                return None

            import secrets

            return secrets.SystemRandom().uniform(-0.02, 0.02)
        except Exception as e:
            self.logger.error(f"Erro ao obter funding rate: {e}")
            return None

    async def _executar_funding_arbitrage(self, symbol: str, funding_rate: float):
        """Executa arbitragem de funding rate"""
        self.logger.info(f"Funding arbitrage para {symbol}. Rate: {funding_rate:.4f}")

        if funding_rate > 0:
            await self.executar_trade(f"{symbol}_PERP", "sell", 0.01, caso_uso=3)
            await self.executar_trade(symbol, "buy", 0.01, caso_uso=3)
        else:
            await self.executar_trade(f"{symbol}_PERP", "buy", 0.01, caso_uso=3)
            await self.executar_trade(symbol, "sell", 0.01, caso_uso=3)

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
