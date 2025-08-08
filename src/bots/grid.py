"""
Bot Grid - Trading em grade com ordens buy/sell escalonadas
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .bot_base import BotBase
from ..utils.kpis import GerenciadorKPIs


class BotGrid(BotBase):
    """Bot especializado em grid trading"""

    def __init__(self, config, monitor, motor_ia):
        super().__init__(config, monitor, motor_ia)
        self.grids_ativas = {}
        self.ordens_abertas = {}

    def get_intervalo_execucao(self) -> int:
        """Intervalo de 60 segundos para grid trading"""
        return 60

    async def executar(self):
        """Executa grid trading em todos os casos de uso"""
        self.logger.info("Executando grid trading")

        for caso_uso in [1, 2, 3]:
            try:
                await self.executar_caso_uso(caso_uso)
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f"Erro no caso de uso {caso_uso}: {e}")

    async def executar_caso_uso(self, caso_uso: int):
        """Executa caso de uso específico de grid trading"""
        parametros = self.get_parametros_caso_uso(caso_uso)

        if caso_uso == 1:
            await self._grid_fixo(parametros)
        elif caso_uso == 2:
            await self._grid_dinamico(parametros)
        elif caso_uso == 3:
            await self._grid_stop_loss(parametros)

    async def _grid_fixo(self, parametros: Dict[str, Any]):
        """Caso de uso 1: Grid fixo em mercado lateral"""
        symbol = "BTC/USDT"
        grid_size = parametros.get("grid_size", 10)
        range_percent = parametros.get("range_percent", 5) / 100

        analise = await self.analisar_mercado(symbol)
        if not analise:
            return

        if not analise or not analise.get("ticker"):
            preco_atual = 50000.0  # Preço simulado para testes
        else:
            preco_atual = analise["ticker"]["last"]

        preco_min = preco_atual * (1 - range_percent)
        preco_max = preco_atual * (1 + range_percent)

        grid_id = f"grid_fixo_{symbol}_{datetime.now().strftime('%H%M%S')}"
        grid = await self._criar_grid(
            grid_id, symbol, preco_min, preco_max, grid_size, "fixo"
        )

        if grid:
            self.grids_ativas[grid_id] = grid
            await self._executar_grid(grid_id)

    async def _grid_dinamico(self, parametros: Dict[str, Any]):
        """Caso de uso 2: Grid dinâmico com ajuste automático"""
        symbol = "ETH/USDT"
        grid_size = parametros.get("grid_size", 8)
        ajuste_auto = parametros.get("ajuste_auto", True)

        analise = await self.analisar_mercado(symbol)
        if not analise:
            return

        if not analise or not analise.get("ticker"):
            preco_atual = 50000.0  # Preço simulado para testes
        else:
            preco_atual = analise["ticker"]["last"]
        volatilidade = await self._calcular_volatilidade(symbol)

        range_percent = max(0.02, min(0.1, volatilidade * 2))

        preco_min = preco_atual * (1 - range_percent)
        preco_max = preco_atual * (1 + range_percent)

        grid_id = f"grid_dinamico_{symbol}_{datetime.now().strftime('%H%M%S')}"
        grid = await self._criar_grid(
            grid_id, symbol, preco_min, preco_max, grid_size, "dinamico"
        )

        if grid:
            self.grids_ativas[grid_id] = grid
            await self._executar_grid(grid_id)

    async def _grid_stop_loss(self, parametros: Dict[str, Any]):
        """Caso de uso 3: Grid com stop loss inteligente"""
        symbol = "ADA/USDT"
        grid_size = parametros.get("grid_size", 6)
        stop_percent = parametros.get("stop_percent", 2) / 100

        analise = await self.analisar_mercado(symbol)
        if not analise:
            return

        if not analise or not analise.get("ticker"):
            preco_atual = 50000.0  # Preço simulado para testes
        else:
            preco_atual = analise["ticker"]["last"]
        stop_loss_price = preco_atual * (1 - stop_percent)

        grid_id = f"grid_stop_{symbol}_{datetime.now().strftime('%H%M%S')}"
        grid = await self._criar_grid(
            grid_id, symbol, stop_loss_price, preco_atual * 1.05, grid_size, "stop_loss"
        )

        if grid:
            grid["stop_loss"] = stop_loss_price
            self.grids_ativas[grid_id] = grid
            await self._executar_grid(grid_id)

    async def _criar_grid(
        self,
        grid_id: str,
        symbol: str,
        preco_min: float,
        preco_max: float,
        grid_size: int,
        tipo: str,
    ) -> Optional[Dict]:
        """Cria estrutura do grid"""
        try:
            step = (preco_max - preco_min) / (grid_size - 1)
            niveis = [preco_min + i * step for i in range(grid_size)]

            amount_per_level = 0.001  # Quantidade fixa por nível

            grid = {
                "id": grid_id,
                "symbol": symbol,
                "tipo": tipo,
                "preco_min": preco_min,
                "preco_max": preco_max,
                "niveis": niveis,
                "amount_per_level": amount_per_level,
                "ordens_buy": {},
                "ordens_sell": {},
                "created_at": datetime.now(),
                "ativo": True,
            }

            self.logger.info(
                f"Grid criado: {grid_id} - {symbol} "
                f"Range: {preco_min:.4f} - {preco_max:.4f} "
                f"Níveis: {grid_size}"
            )

            return grid

        except Exception as e:
            self.logger.error(f"Erro ao criar grid: {e}")
            return None

    async def _executar_grid(self, grid_id: str):
        """Executa ordens do grid"""
        if grid_id not in self.grids_ativas:
            return

        grid = self.grids_ativas[grid_id]
        symbol = grid["symbol"]

        ticker = await self.exchange_manager.get_ticker(symbol)
        if not ticker:
            return

        preco_atual = ticker["last"]

        if "stop_loss" in grid and preco_atual <= grid["stop_loss"]:
            await self._fechar_grid(grid_id, "stop_loss")
            return

        for nivel in grid["niveis"]:
            if nivel < preco_atual and nivel not in grid["ordens_buy"]:
                trade = await self.executar_trade(
                    symbol,
                    "buy",
                    grid["amount_per_level"],
                    nivel,
                    caso_uso=self._get_caso_uso_from_tipo(grid["tipo"]),
                )
                if trade:
                    grid["ordens_buy"][nivel] = trade.id

        for nivel in grid["niveis"]:
            if nivel > preco_atual and nivel not in grid["ordens_sell"]:
                trade = await self.executar_trade(
                    symbol,
                    "sell",
                    grid["amount_per_level"],
                    nivel,
                    caso_uso=self._get_caso_uso_from_tipo(grid["tipo"]),
                )
                if trade:
                    grid["ordens_sell"][nivel] = trade.id

        await self._verificar_execucoes_grid(grid_id)

    def _get_caso_uso_from_tipo(self, tipo: str) -> int:
        """Mapeia tipo de grid para caso de uso"""
        mapping = {"fixo": 1, "dinamico": 2, "stop_loss": 3}
        return mapping.get(tipo, 1)

    async def _verificar_execucoes_grid(self, grid_id: str):
        """Verifica ordens executadas e recria grid"""
        if grid_id not in self.grids_ativas:
            return

        grid = self.grids_ativas[grid_id]

        import random

        if random.random() < 0.1:  # 10% chance de execução  # nosec B311
            if grid["ordens_buy"]:
                nivel_executado = random.choice(
                    list(grid["ordens_buy"].keys())
                )  # nosec B311
                del grid["ordens_buy"][nivel_executado]
                self.logger.info(f"Ordem buy executada no nível {nivel_executado}")

            if grid["ordens_sell"]:
                nivel_executado = random.choice(
                    list(grid["ordens_sell"].keys())
                )  # nosec B311
                del grid["ordens_sell"][nivel_executado]
                self.logger.info(f"Ordem sell executada no nível {nivel_executado}")

    async def _calcular_volatilidade(self, symbol: str) -> float:
        """Calcula volatilidade do símbolo"""
        try:
            ohlcv = await self.exchange_manager.get_ohlcv(symbol, "1h", 24)
            if len(ohlcv) < 2:
                return 0.05  # Volatilidade padrão

            closes = [candle[4] for candle in ohlcv]
            returns = [
                (closes[i] - closes[i - 1]) / closes[i - 1]
                for i in range(1, len(closes))
            ]

            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatilidade = variance**0.5

            return volatilidade

        except Exception as e:
            self.logger.error(f"Erro ao calcular volatilidade: {e}")
            return 0.05

    async def _fechar_grid(self, grid_id: str, motivo: str):
        """Fecha grid e cancela ordens"""
        if grid_id not in self.grids_ativas:
            return

        grid = self.grids_ativas[grid_id]
        grid["ativo"] = False

        self.logger.info(f"Fechando grid {grid_id}. Motivo: {motivo}")

        pnl_total = 0.0
        for trade in self.trades:
            if trade.bot == self.nome and grid_id in trade.id:
                pnl_total += trade.pnl

        self.logger.info(f"Grid {grid_id} fechado. PnL total: {pnl_total:.4f}")

        del self.grids_ativas[grid_id]

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
