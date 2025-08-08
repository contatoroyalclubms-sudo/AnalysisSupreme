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
    
    async def inicializar(self):
        """Inicializa o gerenciador e todos os bots"""
        logger.info("Inicializando gerenciador de bots")
        
        bot_classes = {
            "arbitragem": BotArbitragem,
            "grid": BotGrid,
            "momentum": BotMomentum,
            "scalping": BotScalping,
            "mean_reversion": BotMeanReversion,
            "swing": BotSwing
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
            task = asyncio.create_task(
                self._executar_bot_loop_otimizado(nome, bot),
                name=f"bot_{nome}"
            )
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
        """Loop de execução otimizado de um bot"""
        logger.info(f"Iniciando loop otimizado do bot {nome}")
        
        performance_config = {
            'arbitragem': {'max_concurrent': 3, 'batch_size': 5},
            'scalping': {'max_concurrent': 5, 'batch_size': 10},
            'grid': {'max_concurrent': 2, 'batch_size': 3},
            'momentum': {'max_concurrent': 2, 'batch_size': 3},
            'mean_reversion': {'max_concurrent': 2, 'batch_size': 3},
            'swing': {'max_concurrent': 1, 'batch_size': 2}
        }
        
        config = performance_config.get(nome, {'max_concurrent': 2, 'batch_size': 3})
        semaphore = asyncio.Semaphore(config['max_concurrent'])
        
        while self._running:
            try:
                if hasattr(bot, 'executar_casos_paralelos'):
                    await bot.executar_casos_paralelos(semaphore, config['batch_size'])
                else:
                    async with semaphore:
                        await bot.executar()
                
                intervalo = self._calcular_intervalo_dinamico(nome, bot)
                await asyncio.sleep(intervalo)
                
            except Exception as e:
                logger.error(f"Erro no loop otimizado do bot {nome}: {e}")
                await asyncio.sleep(30)
    
    def _calcular_intervalo_dinamico(self, nome: str, bot: BotBase) -> float:
        """Calcula intervalo dinâmico baseado na performance do bot"""
        base_interval = bot.get_intervalo_execucao()
        
        if hasattr(bot, 'kpi_manager'):
            kpis = bot.kpi_manager.kpis.get(nome, {})
            
            if nome == 'arbitragem' and hasattr(kpis, 'latencia_ms'):
                if kpis.latencia_ms < 30:
                    return base_interval * 0.8
                elif kpis.latencia_ms > 100:
                    return base_interval * 1.5
                    
            elif nome == 'scalping' and hasattr(kpis, 'latencia_ultra'):
                if kpis.latencia_ultra < 20:
                    return base_interval * 0.7
                elif kpis.latencia_ultra > 50:
                    return base_interval * 2.0
        
        return base_interval
    
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
                "status": bot.get_status()
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
            "por_bot": {}
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
                "win_rate": bot_wins / bot_trades if bot_trades > 0 else 0
            }
        
        if total_trades > 0:
            metricas["win_rate"] = total_wins / total_trades
        
        return metricas
    
    async def finalizar(self):
        """Finaliza o gerenciador e todos os bots"""
        logger.info("Finalizando gerenciador de bots")
        
        await self.parar_todos()
        
        for bot in self.bots.values():
            await bot.finalizar()
        
        self.bots.clear()
        logger.info("Gerenciador finalizado")
