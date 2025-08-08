"""
Sistema de monitoramento e observabilidade
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import asdict

from ..core.configuracao import Configuracao
from ..models.trade import Trade

logger = logging.getLogger(__name__)


class Monitor:
    """Sistema de monitoramento e métricas"""

    def __init__(self, config: Configuracao):
        self.config = config
        self.obs_config = config.get_observabilidade_config()
        self.metricas = {}
        self.alertas = []
        self.bots_registrados = set()
        self.trades_por_bot = {}
        self.metricas_sistema = {}
        self._running = False

    async def inicializar(self):
        """Inicializa sistema de monitoramento"""
        logger.info("Inicializando sistema de monitoramento")

        self.metricas = {
            "sistema": {
                "inicio": datetime.now(),
                "uptime": 0,
                "total_trades": 0,
                "pnl_total": 0.0,
                "bots_ativos": 0,
            },
            "por_bot": {},
            "alertas": [],
            "performance": {
                "win_rate_global": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
            },
        }

        if self.obs_config.metricas_ativas:
            await self._inicializar_servidor_metricas()

        logger.info("Sistema de monitoramento inicializado")

    async def _inicializar_servidor_metricas(self):
        """Inicializa servidor Prometheus"""
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Histogram

            self.prometheus_metrics = {
                "trades_total": Counter(
                    "trades_total",
                    "Total de trades executados",
                    ["bot", "symbol", "side"],
                ),
                "pnl_total": Gauge("pnl_total", "PnL total", ["bot"]),
                "win_rate": Gauge("win_rate", "Taxa de vitória", ["bot"]),
                "active_bots": Gauge("active_bots", "Número de bots ativos"),
                "trade_duration": Histogram(
                    "trade_duration_seconds", "Duração dos trades", ["bot"]
                ),
            }

            start_http_server(self.obs_config.prometheus_port)
            logger.info(
                f"Servidor Prometheus iniciado na porta {self.obs_config.prometheus_port}"
            )

        except ImportError:
            logger.warning("Prometheus client não disponível")
        except Exception as e:
            logger.error(f"Erro ao inicializar servidor de métricas: {e}")

    async def registrar_bot(self, nome_bot: str):
        """Registra um bot no sistema de monitoramento"""
        self.bots_registrados.add(nome_bot)
        self.trades_por_bot[nome_bot] = []
        self.metricas["por_bot"][nome_bot] = {
            "total_trades": 0,
            "trades_vencedores": 0,
            "pnl_total": 0.0,
            "ultima_atividade": datetime.now(),
            "status": "ativo",
            "win_rate": 0.0,
            "avg_trade_duration": 0.0,
        }

        logger.info(f"Bot {nome_bot} registrado no monitoramento")

    async def registrar_trade(self, trade: Trade):
        """Registra um trade no sistema"""
        bot_name = trade.bot

        if bot_name not in self.trades_por_bot:
            self.trades_por_bot[bot_name] = []

        self.trades_por_bot[bot_name].append(trade)

        if bot_name in self.metricas["por_bot"]:
            bot_metrics = self.metricas["por_bot"][bot_name]
            bot_metrics["total_trades"] += 1
            bot_metrics["pnl_total"] += trade.pnl
            bot_metrics["ultima_atividade"] = datetime.now()

            if trade.pnl > 0:
                bot_metrics["trades_vencedores"] += 1

            if bot_metrics["total_trades"] > 0:
                bot_metrics["win_rate"] = (
                    bot_metrics["trades_vencedores"] / bot_metrics["total_trades"]
                )

        self.metricas["sistema"]["total_trades"] += 1
        self.metricas["sistema"]["pnl_total"] += trade.pnl

        if hasattr(self, "prometheus_metrics"):
            self.prometheus_metrics["trades_total"].labels(
                bot=bot_name, symbol=trade.symbol, side=trade.side
            ).inc()

            self.prometheus_metrics["pnl_total"].labels(bot=bot_name).set(
                self.metricas["por_bot"][bot_name]["pnl_total"]
            )

        await self._verificar_alertas(trade)

        logger.info(
            f"Trade registrado: {bot_name} - {trade.symbol} - PnL: {trade.pnl:.4f}"
        )

    async def _verificar_alertas(self, trade: Trade):
        """Verifica condições de alerta"""
        try:
            if trade.pnl < -100:  # Perda maior que $100
                await self._criar_alerta(
                    "PERDA_SIGNIFICATIVA",
                    f"Trade com perda de ${trade.pnl:.2f} no bot {trade.bot}",
                    "high",
                )

            bot_metrics = self.metricas["por_bot"].get(trade.bot, {})
            ultima_atividade = bot_metrics.get("ultima_atividade")
            if ultima_atividade:
                tempo_inativo = (datetime.now() - ultima_atividade).total_seconds()
                if tempo_inativo > 3600:  # 1 hora inativo
                    await self._criar_alerta(
                        "BOT_INATIVO",
                        f"Bot {trade.bot} inativo há {tempo_inativo/3600:.1f} horas",
                        "medium",
                    )

            if bot_metrics.get("total_trades", 0) > 20:
                win_rate = bot_metrics.get("win_rate", 0)
                if win_rate < 0.3:  # Win rate menor que 30%
                    await self._criar_alerta(
                        "WIN_RATE_BAIXO",
                        f"Bot {trade.bot} com win rate de {win_rate:.1%}",
                        "medium",
                    )

        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")

    async def _criar_alerta(self, tipo: str, mensagem: str, severidade: str):
        """Cria um alerta"""
        alerta = {
            "tipo": tipo,
            "mensagem": mensagem,
            "severidade": severidade,
            "timestamp": datetime.now(),
            "resolvido": False,
        }

        self.alertas.append(alerta)
        self.metricas["alertas"].append(alerta)

        logger.warning(f"ALERTA [{severidade.upper()}]: {mensagem}")

    async def executar_monitoramento(self):
        """Executa loop de monitoramento"""
        logger.info("Iniciando loop de monitoramento")
        self._running = True

        while self._running:
            try:
                await self._atualizar_metricas_sistema()
                await self._calcular_metricas_performance()
                await self._verificar_saude_sistema()
                await self._gerar_relatorio_periodico()

                await asyncio.sleep(60)  # Atualizar a cada minuto

            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(60)

    async def _atualizar_metricas_sistema(self):
        """Atualiza métricas do sistema"""
        try:
            inicio = self.metricas["sistema"]["inicio"]
            self.metricas["sistema"]["uptime"] = (
                datetime.now() - inicio
            ).total_seconds()
            self.metricas["sistema"]["bots_ativos"] = len(
                [
                    bot
                    for bot, metrics in self.metricas["por_bot"].items()
                    if metrics["status"] == "ativo"
                ]
            )

            if hasattr(self, "prometheus_metrics"):
                self.prometheus_metrics["active_bots"].set(
                    self.metricas["sistema"]["bots_ativos"]
                )

        except Exception as e:
            logger.error(f"Erro ao atualizar métricas do sistema: {e}")

    async def _calcular_metricas_performance(self):
        """Calcula métricas de performance"""
        try:
            todos_trades = []
            for trades_bot in self.trades_por_bot.values():
                todos_trades.extend(trades_bot)

            if not todos_trades:
                return

            trades_vencedores = len([t for t in todos_trades if t.pnl > 0])
            win_rate_global = trades_vencedores / len(todos_trades)

            total_wins = sum(t.pnl for t in todos_trades if t.pnl > 0)
            total_losses = abs(sum(t.pnl for t in todos_trades if t.pnl < 0))
            profit_factor = total_wins / total_losses if total_losses > 0 else 0

            returns = [t.pnl for t in todos_trades]
            if len(returns) > 1:
                mean_return = sum(returns) / len(returns)
                std_return = (
                    sum((r - mean_return) ** 2 for r in returns) / len(returns)
                ) ** 0.5
                sharpe_ratio = mean_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0

            cumulative_pnl = 0
            peak = 0
            max_drawdown = 0

            for trade in todos_trades:
                cumulative_pnl += trade.pnl
                if cumulative_pnl > peak:
                    peak = cumulative_pnl
                drawdown = (peak - cumulative_pnl) / peak if peak > 0 else 0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            self.metricas["performance"].update(
                {
                    "win_rate_global": win_rate_global,
                    "profit_factor": profit_factor,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown,
                }
            )

        except Exception as e:
            logger.error(f"Erro ao calcular métricas de performance: {e}")

    async def _verificar_saude_sistema(self):
        """Verifica saúde geral do sistema"""
        try:
            if self.metricas["sistema"]["bots_ativos"] == 0:
                await self._criar_alerta(
                    "NENHUM_BOT_ATIVO", "Nenhum bot está ativo no sistema", "high"
                )

            performance = self.metricas["performance"]
            if (
                performance["win_rate_global"] < 0.4
                and self.metricas["sistema"]["total_trades"] > 50
            ):
                await self._criar_alerta(
                    "PERFORMANCE_BAIXA",
                    f"Win rate global baixo: {performance['win_rate_global']:.1%}",
                    "medium",
                )

            if performance["max_drawdown"] > 0.2:  # 20% drawdown
                await self._criar_alerta(
                    "DRAWDOWN_ALTO",
                    f"Drawdown máximo alto: {performance['max_drawdown']:.1%}",
                    "high",
                )

        except Exception as e:
            logger.error(f"Erro ao verificar saúde do sistema: {e}")

    async def _gerar_relatorio_periodico(self):
        """Gera relatório periódico"""
        try:
            agora = datetime.now()
            if agora.minute == 0:  # No início de cada hora
                relatorio = await self.gerar_relatorio_completo()

                timestamp = agora.strftime("%Y%m%d_%H%M")
                relatorio_path = f"logs/relatorio_{timestamp}.json"

                import os

                os.makedirs("logs", exist_ok=True)

                with open(relatorio_path, "w", encoding="utf-8") as f:
                    json.dump(relatorio, f, indent=2, default=str, ensure_ascii=False)

                logger.info(f"Relatório periódico salvo: {relatorio_path}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório periódico: {e}")

    async def gerar_relatorio_completo(self) -> Dict[str, Any]:
        """Gera relatório completo do sistema"""
        try:
            relatorio = {
                "timestamp": datetime.now(),
                "sistema": self.metricas["sistema"].copy(),
                "performance": self.metricas["performance"].copy(),
                "bots": {},
                "alertas_ativos": [
                    a for a in self.alertas if not a.get("resolvido", False)
                ],
                "resumo": {},
            }

            for bot_name, metrics in self.metricas["por_bot"].items():
                trades_bot = self.trades_por_bot.get(bot_name, [])

                relatorio["bots"][bot_name] = {
                    "metricas": metrics.copy(),
                    "trades_recentes": len(
                        [
                            t
                            for t in trades_bot
                            if (datetime.now() - t.timestamp).total_seconds() < 3600
                        ]
                    ),
                    "melhor_trade": max([t.pnl for t in trades_bot], default=0),
                    "pior_trade": min([t.pnl for t in trades_bot], default=0),
                }

            relatorio["resumo"] = {
                "total_bots": len(self.bots_registrados),
                "bots_ativos": self.metricas["sistema"]["bots_ativos"],
                "trades_ultima_hora": len(
                    [
                        t
                        for trades in self.trades_por_bot.values()
                        for t in trades
                        if (datetime.now() - t.timestamp).total_seconds() < 3600
                    ]
                ),
                "pnl_ultima_hora": sum(
                    [
                        t.pnl
                        for trades in self.trades_por_bot.values()
                        for t in trades
                        if (datetime.now() - t.timestamp).total_seconds() < 3600
                    ]
                ),
                "alertas_ativos": len(
                    [a for a in self.alertas if not a.get("resolvido", False)]
                ),
            }

            return relatorio

        except Exception as e:
            logger.error(f"Erro ao gerar relatório completo: {e}")
            return {}

    async def salvar_metricas_bot(self, nome_bot: str, metricas_finais: Dict):
        """Salva métricas finais de um bot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metricas_path = f"logs/metricas_{nome_bot}_{timestamp}.json"

            import os

            os.makedirs("logs", exist_ok=True)

            with open(metricas_path, "w", encoding="utf-8") as f:
                json.dump(metricas_finais, f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"Métricas finais do bot {nome_bot} salvas: {metricas_path}")

        except Exception as e:
            logger.error(f"Erro ao salvar métricas do bot {nome_bot}: {e}")

    def get_metricas_tempo_real(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        return {
            "timestamp": datetime.now(),
            "sistema": self.metricas["sistema"],
            "performance": self.metricas["performance"],
            "bots_status": {
                bot: {
                    "status": metrics["status"],
                    "total_trades": metrics["total_trades"],
                    "pnl_total": metrics["pnl_total"],
                    "win_rate": metrics["win_rate"],
                }
                for bot, metrics in self.metricas["por_bot"].items()
            },
            "alertas_recentes": self.alertas[-10:],  # Últimos 10 alertas
        }

    async def finalizar(self):
        """Finaliza sistema de monitoramento"""
        logger.info("Finalizando sistema de monitoramento")

        self._running = False

        relatorio_final = await self.gerar_relatorio_completo()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = f"logs/relatorio_final_{timestamp}.json"

        import os

        os.makedirs("logs", exist_ok=True)

        try:
            with open(relatorio_path, "w", encoding="utf-8") as f:
                json.dump(relatorio_final, f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"Relatório final salvo: {relatorio_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar relatório final: {e}")

        logger.info("Sistema de monitoramento finalizado")
