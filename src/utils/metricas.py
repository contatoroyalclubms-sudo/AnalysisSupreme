"""
Calculador de métricas de trading
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..models.trade import Trade


class CalculadorMetricas:
    """Calculador de métricas de performance de trading"""

    def calcular_metricas_finais(self, trades: List[Trade]) -> Dict[str, Any]:
        """Calcula métricas finais de performance"""
        if not trades:
            return self._metricas_vazias()

        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = total_trades - winning_trades

        total_pnl = sum(t.pnl for t in trades)
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        avg_trade = total_pnl / total_trades if total_trades > 0 else 0
        avg_winning_trade = gross_profit / winning_trades if winning_trades > 0 else 0
        avg_losing_trade = -gross_loss / losing_trades if losing_trades > 0 else 0

        largest_win = max([t.pnl for t in trades], default=0)
        largest_loss = min([t.pnl for t in trades], default=0)

        max_consecutive_wins = self._calcular_consecutivos(trades, True)
        max_consecutive_losses = self._calcular_consecutivos(trades, False)

        max_drawdown, max_drawdown_percent = self._calcular_drawdown(trades)

        sharpe_ratio = self._calcular_sharpe_ratio(trades)

        sortino_ratio = self._calcular_sortino_ratio(trades)

        calmar_ratio = self._calcular_calmar_ratio(trades, max_drawdown_percent)

        recovery_factor = total_pnl / abs(max_drawdown) if max_drawdown != 0 else 0

        expectancy = (win_rate * avg_winning_trade) + (
            (1 - win_rate) * avg_losing_trade
        )

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "avg_trade": avg_trade,
            "avg_winning_trade": avg_winning_trade,
            "avg_losing_trade": avg_losing_trade,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown_percent,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "recovery_factor": recovery_factor,
            "expectancy": expectancy,
            "periodo_analise": {
                "inicio": min(t.timestamp for t in trades),
                "fim": max(t.timestamp for t in trades),
                "duracao_dias": (
                    max(t.timestamp for t in trades) - min(t.timestamp for t in trades)
                ).days,
            },
        }

    def _metricas_vazias(self) -> Dict[str, Any]:
        """Retorna métricas vazias"""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": 0.0,
            "avg_trade": 0.0,
            "avg_winning_trade": 0.0,
            "avg_losing_trade": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "max_drawdown": 0.0,
            "max_drawdown_percent": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "recovery_factor": 0.0,
            "expectancy": 0.0,
            "periodo_analise": None,
        }

    def _calcular_consecutivos(self, trades: List[Trade], wins: bool) -> int:
        """Calcula máximo de trades consecutivos vencedores ou perdedores"""
        if not trades:
            return 0

        max_consecutive = 0
        current_consecutive = 0

        for trade in trades:
            if (wins and trade.pnl > 0) or (not wins and trade.pnl <= 0):
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _calcular_drawdown(self, trades: List[Trade]) -> tuple:
        """Calcula drawdown máximo"""
        if not trades:
            return 0.0, 0.0

        trades_ordenados = sorted(trades, key=lambda t: t.timestamp)

        equity = 0
        peak = 0
        max_drawdown = 0
        max_drawdown_percent = 0

        for trade in trades_ordenados:
            equity += trade.pnl

            if equity > peak:
                peak = equity

            drawdown = peak - equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_percent = drawdown / peak if peak > 0 else 0

        return max_drawdown, max_drawdown_percent

    def _calcular_sharpe_ratio(
        self, trades: List[Trade], risk_free_rate: float = 0.02
    ) -> float:
        """Calcula Sharpe ratio"""
        if len(trades) < 2:
            return 0.0

        returns = [t.pnl for t in trades]
        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)

        if std_return == 0:
            return 0.0

        daily_risk_free = risk_free_rate / 365
        sharpe = (mean_return - daily_risk_free) / std_return

        return sharpe * np.sqrt(365)

    def _calcular_sortino_ratio(
        self, trades: List[Trade], risk_free_rate: float = 0.02
    ) -> float:
        """Calcula Sortino ratio"""
        if len(trades) < 2:
            return 0.0

        returns = [t.pnl for t in trades]
        mean_return = np.mean(returns)

        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return float("inf") if mean_return > 0 else 0.0

        downside_deviation = np.std(negative_returns, ddof=1)

        if downside_deviation == 0:
            return 0.0

        daily_risk_free = risk_free_rate / 365
        sortino = (mean_return - daily_risk_free) / downside_deviation

        return sortino * np.sqrt(365)

    def _calcular_calmar_ratio(
        self, trades: List[Trade], max_drawdown_percent: float
    ) -> float:
        """Calcula Calmar ratio"""
        if not trades or max_drawdown_percent == 0:
            return 0.0

        total_pnl = sum(t.pnl for t in trades)
        periodo_dias = (
            max(t.timestamp for t in trades) - min(t.timestamp for t in trades)
        ).days

        if periodo_dias == 0:
            return 0.0

        retorno_anualizado = (total_pnl / periodo_dias) * 365

        return retorno_anualizado / max_drawdown_percent

    def calcular_metricas_periodo(
        self, trades: List[Trade], periodo_dias: int
    ) -> Dict[str, Any]:
        """Calcula métricas para um período específico"""
        if not trades:
            return self._metricas_vazias()

        data_limite = datetime.now() - timedelta(days=periodo_dias)
        trades_periodo = [t for t in trades if t.timestamp >= data_limite]

        return self.calcular_metricas_finais(trades_periodo)

    def calcular_metricas_por_symbol(
        self, trades: List[Trade]
    ) -> Dict[str, Dict[str, Any]]:
        """Calcula métricas agrupadas por símbolo"""
        if not trades:
            return {}

        trades_por_symbol = {}
        for trade in trades:
            if trade.symbol not in trades_por_symbol:
                trades_por_symbol[trade.symbol] = []
            trades_por_symbol[trade.symbol].append(trade)

        metricas_por_symbol = {}
        for symbol, symbol_trades in trades_por_symbol.items():
            metricas_por_symbol[symbol] = self.calcular_metricas_finais(symbol_trades)

        return metricas_por_symbol

    def calcular_correlacao_bots(
        self, trades_por_bot: Dict[str, List[Trade]]
    ) -> Dict[str, Dict[str, float]]:
        """Calcula correlação entre performance dos bots"""
        if len(trades_por_bot) < 2:
            return {}

        bot_returns = {}

        for bot_name, trades in trades_por_bot.items():
            if not trades:
                continue

            trades_por_dia = {}
            for trade in trades:
                dia = trade.timestamp.date()
                if dia not in trades_por_dia:
                    trades_por_dia[dia] = 0
                trades_por_dia[dia] += trade.pnl

            bot_returns[bot_name] = trades_por_dia

        correlacoes = {}
        bot_names = list(bot_returns.keys())

        for i, bot1 in enumerate(bot_names):
            correlacoes[bot1] = {}
            for j, bot2 in enumerate(bot_names):
                if i == j:
                    correlacoes[bot1][bot2] = 1.0
                else:
                    dias_comuns = set(bot_returns[bot1].keys()) & set(
                        bot_returns[bot2].keys()
                    )

                    if len(dias_comuns) < 2:
                        correlacoes[bot1][bot2] = 0.0
                    else:
                        returns1 = [bot_returns[bot1][dia] for dia in dias_comuns]
                        returns2 = [bot_returns[bot2][dia] for dia in dias_comuns]

                        correlacao = np.corrcoef(returns1, returns2)[0, 1]
                        correlacoes[bot1][bot2] = (
                            correlacao if not np.isnan(correlacao) else 0.0
                        )

        return correlacoes

    def calcular_metricas(self, trades: List[Trade]) -> Dict[str, Any]:
        """Método simplificado para calcular métricas básicas"""
        if not trades:
            return {"total_trades": 0, "win_rate": 0.0, "pnl_total": 0.0}

        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        pnl_total = sum(t.pnl for t in trades)

        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "pnl_total": pnl_total,
        }

    def calcular_sharpe_ratio(self, returns: List[float]) -> float:
        """Calcula Sharpe ratio simplificado"""
        if len(returns) < 2:
            return 0.0

        import numpy as np

        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)

        if std_return == 0:
            return 0.0

        return mean_return / std_return

    def calcular_sortino_ratio(self, returns: List[float]) -> float:
        """Calcula Sortino ratio simplificado"""
        if len(returns) < 2:
            return 0.0

        import numpy as np

        mean_return = np.mean(returns)
        negative_returns = [r for r in returns if r < 0]

        if not negative_returns:
            return float("inf") if mean_return > 0 else 0.0

        downside_deviation = np.std(negative_returns, ddof=1)

        if downside_deviation == 0:
            return 0.0

        return mean_return / downside_deviation

    def calcular_drawdown(self, returns: List[float]) -> float:
        """Calcula drawdown máximo simplificado"""
        if not returns:
            return 0.0

        cumulative = 0
        peak = 0
        max_drawdown = 0

        for ret in returns:
            cumulative += ret
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown
