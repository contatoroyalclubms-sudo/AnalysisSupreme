"""
Gerenciador central dos bots de trading
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .configuracao import Configuracao
from ..bots.bot_base import BotBase
from ..bots.arbitragem import BotArbitragem
from ..bots.grid import BotGrid
from ..bots.momentum import BotMomentum
from ..bots.scalping import BotScalping
from ..bots.mean_reversion import BotMeanReversion
from ..bots.swing import BotSwing
from ..observabilidade.monitor import Monitor
from ..ia.motor_ia import MotorIA
from .engine.sinfonia_suprema import SinfoniaSuprema, get_sinfonia_suprema
from .engine.ultra_fast_executor import UltraFastExecutor, ExecutionTask
from .engine.websocket_manager_premium import WebSocketManagerPremium
from .engine.cache_intelligence import CacheIntelligence
from .engine.memory_optimizer import MemoryOptimizer
from .engine.cryptobot_orchestrator import CryptoBotOrchestrator, BotConfig
import time

logger = logging.getLogger(__name__)


class GerenciadorBots:
    """Gerenciador central dos bots de trading"""

    def __init__(self, config: Configuracao, monitor: Monitor, motor_ia: MotorIA):
        self.config = config
        self.monitor = monitor
        self.motor_ia = motor_ia
        self.bots: Dict[str, BotBase] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self._running = False

        self.sinfonia_suprema: Optional[SinfoniaSuprema] = None

        bot_config = BotConfig(
            max_concurrent_trades=50,
            risk_per_trade=0.02,
            max_daily_risk=0.10,
            min_confidence=0.75,
            execution_speed_ms=15,
            profit_target=0.15,
        )
        self.cryptobot_orchestrator = CryptoBotOrchestrator(bot_config)

    async def inicializar(self):
        """🚀 Inicializa CRYPTOBOT SUPREMO GLOBAL - Gerenciador de Bots"""
        logger.info("🚀 Inicializando CRYPTOBOT SUPREMO GLOBAL - Gerenciador de Bots")

        logger.info("🎼 Inicializando Sinfonia Tecnológica Suprema...")
        self.sinfonia_suprema = await get_sinfonia_suprema()
        logger.info("✅ Sinfonia Tecnológica Suprema inicializada")

        await self.cryptobot_orchestrator.initialize_supreme_system()
        logger.info("🚀 CryptoBotOrchestrator Quantum System inicializado")

        bot_classes = {
            "arbitragem": BotArbitragem,
            "grid": BotGrid,
            "momentum": BotMomentum,
            "scalping": BotScalping,
            "mean_reversion": BotMeanReversion,
            "swing": BotSwing,
        }

        for nome, bot_class in bot_classes.items():
            bot_config = self.config.get_bot_config(nome)
            if bot_config and bot_config.ativo:
                try:
                    bot = bot_class(self.config, self.monitor, self.motor_ia)
                    await bot.inicializar()
                    self.bots[nome] = bot
                    logger.info(f"Bot {nome} inicializado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao inicializar bot {nome}: {e}")

        logger.info(f"Gerenciador inicializado com {len(self.bots)} bots ativos")

    async def executar_bot(self, nome_bot: str, caso_uso: Optional[int] = None):
        """Executa um bot específico"""
        if nome_bot not in self.bots:
            raise ValueError(f"Bot {nome_bot} não encontrado ou não ativo")

        bot = self.bots[nome_bot]
        logger.info(f"Executando bot {nome_bot}")

        try:
            if caso_uso:
                await bot.executar_caso_uso(caso_uso)
            else:
                await bot.executar()
        except Exception as e:
            logger.error(f"Erro ao executar bot {nome_bot}: {e}")
            raise

    async def executar_todos(self):
        """Executa todos os bots ativos concorrentemente com otimizações de performance"""
        if not self.bots:
            logger.warning("Nenhum bot ativo para executar")
            return

        logger.info(f"Executando {len(self.bots)} bots em paralelo")
        self._running = True

        tasks = []
        for nome, bot in self.bots.items():
            task = asyncio.create_task(self._executar_bot_loop_otimizado(nome, bot), name=f"bot_{nome}")
            self.tasks[nome] = task
            tasks.append(task)

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Erro na execução paralela dos bots: {e}")
        finally:
            self._running = False

    async def _executar_bot_loop(self, nome: str, bot: BotBase):
        """Loop de execução de um bot"""
        logger.info(f"Iniciando loop do bot {nome}")

        while self._running:
            try:
                await bot.executar()

                intervalo = bot.get_intervalo_execucao()
                await asyncio.sleep(intervalo)

            except Exception as e:
                logger.error(f"Erro no loop do bot {nome}: {e}")
                await asyncio.sleep(60)

    async def _executar_bot_loop_otimizado(self, nome: str, bot: BotBase):
        """🎼 SINFONIA TECNOLÓGICA - Loop de execução ultra otimizado"""
        logger.info(f"🎼 Iniciando Sinfonia Tecnológica para bot {nome}")

        while self._running:
            try:
                start_time = time.time() * 1000

                if self.sinfonia_suprema:
                    result = await self.sinfonia_suprema.execute_movimento(nome, bot.executar, {})
                    logger.debug(f"⚡ {nome} executado via Sinfonia Suprema")
                else:
                    if hasattr(bot, "executar_casos_paralelos"):
                        semaphore = asyncio.Semaphore(3)
                        await bot.executar_casos_paralelos(semaphore, 5)
                    else:
                        await bot.executar()

                execution_time = time.time() * 1000 - start_time

                intervalo = self._calcular_intervalo_sinfonia(nome, bot, execution_time)
                await asyncio.sleep(intervalo)

            except Exception as e:
                logger.error(f"❌ Erro na Sinfonia Tecnológica do bot {nome}: {e}")
                await asyncio.sleep(15)  # Recovery mais rápido

    def _calcular_intervalo_sinfonia(self, nome: str, bot: BotBase, execution_time: float) -> float:
        """🎼 MOVIMENTO IV: Finale - Cálculo de Intervalo Sinfônico"""
        base_interval = bot.get_intervalo_execucao()

        movimento_intervals = {
            "arbitragem": 0.5,  # Presto - Ultra rápido
            "scalping": 0.7,  # Allegro - Muito rápido
            "momentum": 0.8,  # Allegro - Rápido
            "grid": 1.0,  # Andante - Moderado
            "mean_reversion": 1.2,  # Andante - Moderado
            "swing": 1.5,  # Largo - Lento e preciso
        }

        movimento_factor = movimento_intervals.get(nome, 1.0)

        if execution_time <= 15:  # Ultra performance
            adjustment = 0.6
        elif execution_time <= 50:  # Boa performance
            adjustment = 0.8
        elif execution_time <= 100:  # Performance aceitável
            adjustment = 1.0
        else:  # Performance ruim
            adjustment = 1.5

        final_interval = base_interval * movimento_factor * adjustment

        min_intervals = {
            "arbitragem": 0.01,  # 10ms mínimo
            "scalping": 0.02,  # 20ms mínimo
            "grid": 0.1,  # 100ms mínimo
            "momentum": 0.05,  # 50ms mínimo
            "mean_reversion": 0.2,  # 200ms mínimo
            "swing": 1.0,  # 1s mínimo
        }

        max_intervals = {
            "arbitragem": 0.5,  # 500ms máximo
            "scalping": 1.0,  # 1s máximo
            "grid": 5.0,  # 5s máximo
            "momentum": 3.0,  # 3s máximo
            "mean_reversion": 10.0,  # 10s máximo
            "swing": 60.0,  # 60s máximo
        }

        min_interval = min_intervals.get(nome, 0.1)
        max_interval = max_intervals.get(nome, 5.0)

        return max(min_interval, min(final_interval, max_interval))

    async def parar_bot(self, nome_bot: str):
        """Para um bot específico"""
        if nome_bot in self.tasks:
            self.tasks[nome_bot].cancel()
            del self.tasks[nome_bot]
            logger.info(f"Bot {nome_bot} parado")

    async def parar_todos(self):
        """Para todos os bots"""
        logger.info("Parando todos os bots")
        self._running = False

        for task in self.tasks.values():
            task.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)

        self.tasks.clear()

    async def reiniciar_bot(self, nome_bot: str):
        """Reinicia um bot específico"""
        if nome_bot in self.bots:
            await self.parar_bot(nome_bot)
            await asyncio.sleep(1)

            bot = self.bots[nome_bot]
            task = asyncio.create_task(self._executar_bot_loop(nome_bot, bot))
            self.tasks[nome_bot] = task

            logger.info(f"Bot {nome_bot} reiniciado")

    def get_status_bots(self) -> Dict[str, Any]:
        """Retorna status de todos os bots"""
        status = {}

        for nome, bot in self.bots.items():
            status[nome] = {
                "ativo": nome in self.tasks and not self.tasks[nome].done(),
                "ultima_execucao": bot.get_ultima_execucao(),
                "total_trades": bot.get_total_trades(),
                "pnl_total": bot.get_pnl_total(),
                "status": bot.get_status(),
            }

        return status

    def get_metricas_consolidadas(self) -> Dict[str, Any]:
        """Retorna métricas consolidadas de todos os bots"""
        metricas = {
            "total_bots": len(self.bots),
            "bots_ativos": len([t for t in self.tasks.values() if not t.done()]),
            "total_trades": 0,
            "pnl_total": 0.0,
            "win_rate": 0.0,
            "por_bot": {},
        }

        total_wins = 0
        total_trades = 0

        for nome, bot in self.bots.items():
            bot_trades = bot.get_total_trades()
            bot_pnl = bot.get_pnl_total()
            bot_wins = bot.get_total_wins()

            metricas["total_trades"] += bot_trades
            metricas["pnl_total"] += bot_pnl
            total_wins += bot_wins
            total_trades += bot_trades

            metricas["por_bot"][nome] = {
                "trades": bot_trades,
                "pnl": bot_pnl,
                "wins": bot_wins,
                "win_rate": bot_wins / bot_trades if bot_trades > 0 else 0,
            }

        if total_trades > 0:
            metricas["win_rate"] = total_wins / total_trades

        return metricas

    async def finalizar(self):
        """🎼 FINALE - Finaliza o CRYPTOBOT SUPREMO GLOBAL"""
        logger.info("🎼 Executando Finale da Sinfonia Tecnológica...")

        await self.parar_todos()

        if self.sinfonia_suprema:
            await self.sinfonia_suprema.finale_graceful_shutdown()
            logger.info("✅ Sinfonia Tecnológica Suprema finalizada")

        await self.cryptobot_orchestrator.shutdown()
        logger.info("🚀 CryptoBotOrchestrator Quantum System finalizado")

        for bot in self.bots.values():
            await bot.finalizar()

        self.bots.clear()
        logger.info("🎼 Finale executado - CRYPTOBOT SUPREMO GLOBAL finalizado com glória!")
