#!/usr/bin/env python3
"""
AnalysisSupreme - Sistema de Trading Automatizado
Sistema completo com 6 bots especializados e IA avançada
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, List

from src.core.gerenciador_bots import GerenciadorBots
from src.core.configuracao import Configuracao
from src.observabilidade.monitor import Monitor
from src.ia.motor_ia import MotorIA
from src.utils.logger import configurar_logger

def criar_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="AnalysisSupreme - Sistema de Trading Automatizado"
    )
    
    parser.add_argument(
        "--bot",
        choices=["arbitragem", "grid", "momentum", "scalping", "mean_reversion", "swing"],
        help="Executar bot específico"
    )
    
    parser.add_argument(
        "--caso-uso",
        type=int,
        choices=[1, 2, 3],
        help="Caso de uso específico (1-3)"
    )
    
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Modo de monitoramento apenas"
    )
    
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Caminho para arquivo de configuração"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nível de logging"
    )
    
    return parser

async def main():
    """Função principal do sistema"""
    parser = criar_parser()
    args = parser.parse_args()
    
    configurar_logger(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        config = Configuracao(args.config)
        logger.info("Configuração carregada com sucesso")
        
        monitor = Monitor(config)
        motor_ia = MotorIA(config)
        gerenciador = GerenciadorBots(config, monitor, motor_ia)
        
        await gerenciador.inicializar()
        await monitor.inicializar()
        await motor_ia.inicializar()
        
        logger.info("AnalysisSupreme iniciado com sucesso")
        
        if args.monitor:
            logger.info("Executando em modo monitoramento")
            await monitor.executar_monitoramento()
        elif args.bot:
            logger.info(f"Executando bot: {args.bot}")
            await gerenciador.executar_bot(args.bot, args.caso_uso)
        else:
            logger.info("Executando todos os bots")
            await gerenciador.executar_todos()
            
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
    finally:
        if 'gerenciador' in locals():
            await gerenciador.finalizar()
        if 'monitor' in locals():
            await monitor.finalizar()
        if 'motor_ia' in locals():
            await motor_ia.finalizar()
        
        logger.info("AnalysisSupreme finalizado")

if __name__ == "__main__":
    asyncio.run(main())
