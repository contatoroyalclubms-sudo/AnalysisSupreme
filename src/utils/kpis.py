"""
Sistema de KPIs específicos por bot
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class KPIArbitragem:
    """KPIs específicos para bot de arbitragem"""

    latencia_ms: float = 0.0
    spread_capturado: float = 0.0
    execucao_simultanea: float = 0.0
    target_latencia: float = 50.0
    target_spread: float = 0.3
    target_execucao: float = 95.0


@dataclass
class KPIGrid:
    """KPIs específicos para bot de grid trading"""

    range_eficiencia: float = 0.0
    grid_adaptabilidade: float = 0.0
    lucro_lateral: float = 0.0
    target_eficiencia: float = 70.0


@dataclass
class KPIMomentum:
    """KPIs específicos para bot de momentum"""

    breakout_precisao: float = 0.0
    false_signal_rate: float = 0.0
    stop_eficiencia: float = 0.0
    target_precisao: float = 65.0
    target_false_signals: float = 30.0
    target_stop: float = 80.0


@dataclass
class KPIScalping:
    """KPIs específicos para bot de scalping"""

    throughput_ops: float = 0.0
    latencia_ultra: float = 0.0
    fee_optimization: float = 0.0
    target_throughput: float = 100.0
    target_latencia: float = 30.0


@dataclass
class KPIMeanReversion:
    """KPIs específicos para bot de mean reversion"""

    reversao_timing: float = 0.0
    oversold_detection: float = 0.0
    rsi_effectiveness: float = 0.0
    target_timing: float = 70.0
    target_oversold: float = 70.0


@dataclass
class KPISwing:
    """KPIs específicos para bot de swing"""

    trend_capture: float = 0.0
    hold_time_optimal: float = 0.0
    pattern_recognition: float = 0.0
    target_capture: float = 60.0


class GerenciadorKPIs:
    """Gerenciador centralizado de KPIs por bot"""

    def __init__(self):
        self.kpis: Dict[str, Any] = {
            "arbitragem": KPIArbitragem(),
            "grid": KPIGrid(),
            "momentum": KPIMomentum(),
            "scalping": KPIScalping(),
            "mean_reversion": KPIMeanReversion(),
            "swing": KPISwing(),
        }
        self.historico: Dict[str, list] = {}
        self.medicoes_ativas: Dict[str, Dict] = {}

    def iniciar_medicao_latencia(self, bot: str, operacao: str) -> str:
        """Inicia medição de latência"""
        medicao_id = f"{bot}_{operacao}_{int(time.time() * 1000)}"
        self.medicoes_ativas[medicao_id] = {
            "bot": bot,
            "operacao": operacao,
            "inicio": time.time() * 1000,
        }
        return medicao_id

    def finalizar_medicao_latencia(self, medicao_id: str) -> float:
        """Finaliza medição de latência e retorna valor em ms"""
        if medicao_id not in self.medicoes_ativas:
            return 0.0

        medicao = self.medicoes_ativas[medicao_id]
        latencia_ms = (time.time() * 1000) - medicao["inicio"]

        bot = medicao["bot"]
        if bot == "arbitragem":
            self.kpis[bot].latencia_ms = latencia_ms
        elif bot == "scalping":
            self.kpis[bot].latencia_ultra = latencia_ms

        del self.medicoes_ativas[medicao_id]
        return latencia_ms

    def atualizar_kpi_arbitragem(self, spread: float, execucao_simultanea: float):
        """Atualiza KPIs específicos de arbitragem"""
        kpi = self.kpis["arbitragem"]
        kpi.spread_capturado = spread
        kpi.execucao_simultanea = execucao_simultanea

        logger.info(
            f"KPI Arbitragem - Spread: {spread:.3f}%, Execução: {execucao_simultanea:.1f}%"
        )

    def atualizar_kpi_grid(
        self, eficiencia: float, adaptabilidade: float, lucro_lateral: float
    ):
        """Atualiza KPIs específicos de grid trading"""
        kpi = self.kpis["grid"]
        kpi.range_eficiencia = eficiencia
        kpi.grid_adaptabilidade = adaptabilidade
        kpi.lucro_lateral = lucro_lateral

        logger.info(
            f"KPI Grid - Eficiência: {eficiencia:.1f}%, Adaptabilidade: {adaptabilidade:.2f}"
        )

    def atualizar_kpi_momentum(
        self, precisao: float, false_signals: float, stop_eficiencia: float
    ):
        """Atualiza KPIs específicos de momentum"""
        kpi = self.kpis["momentum"]
        kpi.breakout_precisao = precisao
        kpi.false_signal_rate = false_signals
        kpi.stop_eficiencia = stop_eficiencia

        logger.info(
            f"KPI Momentum - Precisão: {precisao:.1f}%, False Signals: {false_signals:.1f}%"
        )

    def atualizar_kpi_scalping(self, throughput: float, fee_optimization: float):
        """Atualiza KPIs específicos de scalping"""
        kpi = self.kpis["scalping"]
        kpi.throughput_ops = throughput
        kpi.fee_optimization = fee_optimization

        logger.info(
            f"KPI Scalping - Throughput: {throughput:.1f} ops/min, Fee Opt: {fee_optimization:.2f}"
        )

    def atualizar_kpi_mean_reversion(
        self, timing: float, oversold: float, rsi_effectiveness: float
    ):
        """Atualiza KPIs específicos de mean reversion"""
        kpi = self.kpis["mean_reversion"]
        kpi.reversao_timing = timing
        kpi.oversold_detection = oversold
        kpi.rsi_effectiveness = rsi_effectiveness

        logger.info(
            f"KPI Mean Reversion - Timing: {timing:.1f}%, Oversold: {oversold:.1f}%"
        )

    def atualizar_kpi_swing(
        self, trend_capture: float, hold_time: float, pattern_recognition: float
    ):
        """Atualiza KPIs específicos de swing"""
        kpi = self.kpis["swing"]
        kpi.trend_capture = trend_capture
        kpi.hold_time_optimal = hold_time
        kpi.pattern_recognition = pattern_recognition

        logger.info(
            f"KPI Swing - Trend Capture: {trend_capture:.1f}%, Pattern: {pattern_recognition:.2f}"
        )

    def verificar_targets(self, bot: str) -> Dict[str, bool]:
        """Verifica se KPIs atingem targets"""
        kpi = self.kpis.get(bot)
        if not kpi:
            return {}

        if bot == "arbitragem":
            return {
                "latencia_ok": kpi.latencia_ms < kpi.target_latencia,
                "spread_ok": kpi.spread_capturado > kpi.target_spread,
                "execucao_ok": kpi.execucao_simultanea > kpi.target_execucao,
            }
        elif bot == "grid":
            return {"eficiencia_ok": kpi.range_eficiencia > kpi.target_eficiencia}
        elif bot == "momentum":
            return {
                "precisao_ok": kpi.breakout_precisao > kpi.target_precisao,
                "false_signals_ok": kpi.false_signal_rate < kpi.target_false_signals,
                "stop_ok": kpi.stop_eficiencia > kpi.target_stop,
            }
        elif bot == "scalping":
            return {
                "throughput_ok": kpi.throughput_ops > kpi.target_throughput,
                "latencia_ok": kpi.latencia_ultra < kpi.target_latencia,
            }
        elif bot == "mean_reversion":
            return {
                "timing_ok": kpi.reversao_timing > kpi.target_timing,
                "oversold_ok": kpi.oversold_detection > kpi.target_oversold,
            }
        elif bot == "swing":
            return {"capture_ok": kpi.trend_capture > kpi.target_capture}

        return {}

    def gerar_relatorio_kpis(self) -> Dict[str, Any]:
        """Gera relatório completo de KPIs"""
        relatorio = {"timestamp": datetime.now().isoformat(), "bots": {}}

        for bot_name, kpi in self.kpis.items():
            targets = self.verificar_targets(bot_name)
            targets_atingidos = sum(targets.values())
            total_targets = len(targets)

            relatorio["bots"][bot_name] = {
                "kpis": kpi.__dict__,
                "targets": targets,
                "performance": (
                    f"{targets_atingidos}/{total_targets}"
                    if total_targets > 0
                    else "0/0"
                ),
                "score": (
                    (targets_atingidos / total_targets * 100)
                    if total_targets > 0
                    else 0
                ),
            }

        return relatorio
