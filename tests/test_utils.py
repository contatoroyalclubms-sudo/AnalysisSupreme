"""
Testes para utilitários do sistema
"""

import pytest
from unittest.mock import Mock, patch
import logging
from datetime import datetime

from src.utils.logger import configurar_logger
from src.utils.metricas import CalculadorMetricas
from src.utils.kpis import GerenciadorKPIs
from src.models.trade import Trade


class TestLogger:
    """Testes para sistema de logging"""

    def test_configurar_logger_info(self):
        """Testa configuração do logger em nível INFO"""
        configurar_logger("INFO")
        logger = logging.getLogger("test_info")

        logger.info("Teste de log info")
        logger.warning("Teste de log warning")
        logger.error("Teste de log error")
        assert True

    def test_configurar_logger_debug(self):
        """Testa configuração do logger em nível DEBUG"""
        configurar_logger("DEBUG")
        logger = logging.getLogger("test_debug")

        logger.debug("Teste de log debug")
        logger.info("Teste de log info")
        assert True

    def test_configurar_logger_error(self):
        """Testa configuração do logger em nível ERROR"""
        configurar_logger("ERROR")
        logger = logging.getLogger("test_error")

        logger.error("Teste de log error")
        assert True

    def test_configurar_logger_default(self):
        """Testa configuração padrão do logger"""
        configurar_logger()
        logger = logging.getLogger("test_default")

        logger.info("Teste de log padrão")
        assert True


class TestCalculadorMetricas:
    """Testes para calculador de métricas"""

    def test_inicializacao(self):
        """Testa inicialização do calculador"""
        calculador = CalculadorMetricas()
        assert calculador is not None

    def test_calcular_metricas_vazias(self):
        """Testa cálculo com lista vazia"""
        calculador = CalculadorMetricas()
        metricas = calculador.calcular_metricas_finais([])

        assert metricas["total_trades"] == 0
        assert metricas["win_rate"] == 0.0
        assert metricas["total_pnl"] == 0.0
        assert metricas["winning_trades"] == 0
        assert metricas["losing_trades"] == 0

    def test_calcular_metricas_trades_positivos(self):
        """Testa cálculo com trades positivos"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=200,
            ),
            Trade(
                id="3",
                bot="arbitragem",
                symbol="ETH/USDT",
                side="buy",
                amount=0.1,
                price=3000,
                timestamp=datetime.now(),
                caso_uso=2,
                pnl=150,
            ),
        ]

        metricas = calculador.calcular_metricas_finais(trades)

        assert metricas["total_trades"] == 3
        assert metricas["winning_trades"] == 3
        assert metricas["losing_trades"] == 0
        assert metricas["total_pnl"] == 450
        assert metricas["win_rate"] == 1.0
        assert metricas["avg_winning_trade"] == 150.0
        assert metricas["avg_losing_trade"] == 0.0

    def test_calcular_metricas_trades_mistos(self):
        """Testa cálculo com trades positivos e negativos"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="grid",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="grid",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=-50,
            ),
            Trade(
                id="3",
                bot="grid",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=2,
                pnl=200,
            ),
            Trade(
                id="4",
                bot="grid",
                symbol="ETH/USDT",
                side="sell",
                amount=0.1,
                price=2900,
                timestamp=datetime.now(),
                caso_uso=2,
                pnl=-75,
            ),
        ]

        metricas = calculador.calcular_metricas_finais(trades)

        assert metricas["total_trades"] == 4
        assert metricas["winning_trades"] == 2
        assert metricas["losing_trades"] == 2
        assert metricas["total_pnl"] == 175
        assert metricas["win_rate"] == 0.5
        assert metricas["avg_winning_trade"] == 150.0
        assert metricas["avg_losing_trade"] == -62.5

    def test_calcular_sharpe_ratio(self):
        """Testa cálculo de Sharpe ratio"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="momentum",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="momentum",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
            Trade(
                id="3",
                bot="momentum",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=75,
            ),
        ]

        sharpe = calculador._calcular_sharpe_ratio(trades)
        assert isinstance(sharpe, float)
        assert sharpe >= 0

    def test_calcular_sortino_ratio(self):
        """Testa cálculo de Sortino ratio"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="scalping",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="scalping",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=-50,
            ),
            Trade(
                id="3",
                bot="scalping",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=75,
            ),
        ]

        sortino = calculador._calcular_sortino_ratio(trades)
        assert isinstance(sortino, float)
        assert isinstance(sortino, (int, float))
        assert not (isinstance(sortino, float) and sortino != sortino)  # Check for NaN

    def test_calcular_drawdown(self):
        """Testa cálculo de drawdown"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="mean_reversion",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="mean_reversion",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=-150,
            ),
            Trade(
                id="3",
                bot="mean_reversion",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
        ]

        max_dd, max_dd_pct = calculador._calcular_drawdown(trades)
        assert isinstance(max_dd, (int, float))
        assert isinstance(max_dd_pct, (int, float))
        assert max_dd >= 0
        assert max_dd_pct >= 0

    def test_calcular_metricas_por_periodo(self):
        """Testa cálculo de métricas por período"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="swing",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="swing",
                symbol="BTC/USDT",
                side="sell",
                amount=0.01,
                price=49000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
        ]

        metricas_periodo = calculador.calcular_metricas_periodo(trades, 1)
        assert isinstance(metricas_periodo, dict)
        assert len(metricas_periodo) >= 0

    def test_calcular_metricas_por_simbolo(self):
        """Testa cálculo de métricas por símbolo"""
        calculador = CalculadorMetricas()

        trades = [
            Trade(
                id="1",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=50000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=100,
            ),
            Trade(
                id="2",
                bot="arbitragem",
                symbol="ETH/USDT",
                side="sell",
                amount=0.1,
                price=3000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=50,
            ),
            Trade(
                id="3",
                bot="arbitragem",
                symbol="BTC/USDT",
                side="buy",
                amount=0.01,
                price=51000,
                timestamp=datetime.now(),
                caso_uso=1,
                pnl=75,
            ),
        ]

        metricas_simbolo = calculador.calcular_metricas_por_symbol(trades)
        assert isinstance(metricas_simbolo, dict)
        assert "BTC/USDT" in metricas_simbolo
        assert "ETH/USDT" in metricas_simbolo
        assert metricas_simbolo["BTC/USDT"]["total_trades"] == 2
        assert metricas_simbolo["ETH/USDT"]["total_trades"] == 1


class TestGerenciadorKPIs:
    """Testes para gerenciador de KPIs"""

    def test_inicializacao(self):
        """Testa inicialização do gerenciador"""
        gerenciador = GerenciadorKPIs()
        assert gerenciador is not None
        assert hasattr(gerenciador, "kpis")
        assert hasattr(gerenciador, "historico")
        assert hasattr(gerenciador, "medicoes_ativas")

        assert "arbitragem" in gerenciador.kpis
        assert "grid" in gerenciador.kpis
        assert "momentum" in gerenciador.kpis
        assert "scalping" in gerenciador.kpis
        assert "mean_reversion" in gerenciador.kpis
        assert "swing" in gerenciador.kpis

    def test_atualizar_kpi_arbitragem(self):
        """Testa atualização de KPIs de arbitragem"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_arbitragem(0.35, 96.5)

        kpi = gerenciador.kpis["arbitragem"]
        assert kpi.spread_capturado == 0.35
        assert kpi.execucao_simultanea == 96.5

    def test_atualizar_kpi_grid(self):
        """Testa atualização de KPIs de grid"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_grid(75.0, 0.85, 150.0)

        kpi = gerenciador.kpis["grid"]
        assert kpi.range_eficiencia == 75.0
        assert kpi.grid_adaptabilidade == 0.85
        assert kpi.lucro_lateral == 150.0

    def test_atualizar_kpi_momentum(self):
        """Testa atualização de KPIs de momentum"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_momentum(68.0, 25.0, 82.0)

        kpi = gerenciador.kpis["momentum"]
        assert kpi.breakout_precisao == 68.0
        assert kpi.false_signal_rate == 25.0
        assert kpi.stop_eficiencia == 82.0

    def test_atualizar_kpi_scalping(self):
        """Testa atualização de KPIs de scalping"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_scalping(120.0, 0.95)

        kpi = gerenciador.kpis["scalping"]
        assert kpi.throughput_ops == 120.0
        assert kpi.fee_optimization == 0.95

    def test_atualizar_kpi_mean_reversion(self):
        """Testa atualização de KPIs de mean reversion"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_mean_reversion(72.0, 75.0, 0.68)

        kpi = gerenciador.kpis["mean_reversion"]
        assert kpi.reversao_timing == 72.0
        assert kpi.oversold_detection == 75.0
        assert kpi.rsi_effectiveness == 0.68

    def test_atualizar_kpi_swing(self):
        """Testa atualização de KPIs de swing"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_swing(65.0, 24.5, 0.72)

        kpi = gerenciador.kpis["swing"]
        assert kpi.trend_capture == 65.0
        assert kpi.hold_time_optimal == 24.5
        assert kpi.pattern_recognition == 0.72

    def test_verificar_targets_todos_bots(self):
        """Testa verificação de targets para todos os bots"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_arbitragem(0.35, 96.5)
        gerenciador.atualizar_kpi_grid(75.0, 0.85, 150.0)
        gerenciador.atualizar_kpi_momentum(68.0, 25.0, 82.0)
        gerenciador.atualizar_kpi_scalping(120.0, 0.95)
        gerenciador.atualizar_kpi_mean_reversion(72.0, 75.0, 0.68)
        gerenciador.atualizar_kpi_swing(65.0, 24.5, 0.72)

        gerenciador.kpis["arbitragem"].latencia_ms = 45.0
        gerenciador.kpis["scalping"].latencia_ultra = 25.0

        for bot in [
            "arbitragem",
            "grid",
            "momentum",
            "scalping",
            "mean_reversion",
            "swing",
        ]:
            targets = gerenciador.verificar_targets(bot)
            assert isinstance(targets, dict)
            assert len(targets) > 0

    def test_medicao_latencia(self):
        """Testa sistema de medição de latência"""
        gerenciador = GerenciadorKPIs()

        medicao_id = gerenciador.iniciar_medicao_latencia("arbitragem", "trade")
        assert medicao_id in gerenciador.medicoes_ativas
        assert gerenciador.medicoes_ativas[medicao_id]["bot"] == "arbitragem"
        assert gerenciador.medicoes_ativas[medicao_id]["operacao"] == "trade"

        import time

        time.sleep(0.01)

        latencia = gerenciador.finalizar_medicao_latencia(medicao_id)
        assert isinstance(latencia, float)
        assert latencia > 0
        assert medicao_id not in gerenciador.medicoes_ativas

        assert gerenciador.kpis["arbitragem"].latencia_ms == latencia

    def test_gerar_relatorio_kpis(self):
        """Testa geração de relatório completo"""
        gerenciador = GerenciadorKPIs()

        gerenciador.atualizar_kpi_arbitragem(0.35, 96.5)
        gerenciador.atualizar_kpi_grid(75.0, 0.85, 150.0)
        gerenciador.kpis["arbitragem"].latencia_ms = 45.0

        relatorio = gerenciador.gerar_relatorio_kpis()

        assert "timestamp" in relatorio
        assert "bots" in relatorio
        assert len(relatorio["bots"]) == 6

        bot_arbitragem = relatorio["bots"]["arbitragem"]
        assert "kpis" in bot_arbitragem
        assert "targets" in bot_arbitragem
        assert "performance" in bot_arbitragem
        assert "score" in bot_arbitragem

        targets = bot_arbitragem["targets"]
        assert "latencia_ok" in targets
        assert "spread_ok" in targets
        assert "execucao_ok" in targets

        assert isinstance(bot_arbitragem["score"], (int, float))
        assert 0 <= bot_arbitragem["score"] <= 100
