#!/usr/bin/env python3
"""
Script para executar casos de uso específicos dos bots
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.configuracao import Configuracao
from src.core.gerenciador_bots import GerenciadorBots
from src.observabilidade.monitor import Monitor
from src.ia.motor_ia import MotorIA

async def executar_caso(caso: str):
    """Executa caso de uso específico"""
    print(f"🚀 Executando caso: {caso}")
    
    caso_file = Path(f"logs/casos_uso/{caso}.json")
    if not caso_file.exists():
        print(f"❌ Configuração do caso não encontrada: {caso_file}")
        return False
    
    with open(caso_file, 'r', encoding='utf-8') as f:
        caso_config = json.load(f)
    
    bot_name = caso_config["bot"]
    caso_uso = caso_config["caso_uso"]
    par = caso_config["par"]
    
    print(f"📊 Bot: {bot_name}")
    print(f"📊 Caso de uso: {caso_uso}")
    print(f"📊 Par: {par}")
    print(f"📊 Modo: {'Paper Trading' if caso_config.get('paper_mode', True) else 'Live Trading'}")
    print(f"📊 Objetivo: {caso_config.get('objetivo', 'N/A')}")
    print(f"📊 Latência alvo: {caso_config.get('latencia_alvo', '120ms')}")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/execucao_{caso}.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        config = Configuracao()
        monitor = Monitor(config)
        motor_ia = MotorIA(config)
        gerenciador = GerenciadorBots(config, monitor, motor_ia)
        
        await monitor.inicializar()
        await motor_ia.inicializar()
        await gerenciador.inicializar()
        
        bot = gerenciador.bots.get(bot_name)
        if not bot:
            print(f"❌ Bot {bot_name} não encontrado")
            return False
        
        print(f"✅ Bot {bot_name} inicializado")
        
        print(f"🎯 Executando caso de uso {caso_uso}...")
        await bot.executar_caso_uso(caso_uso)
        
        print("⏳ Aguardando execução (30 segundos)...")
        await asyncio.sleep(30)
        
        relatorio = await monitor.gerar_relatorio_completo()
        
        relatorio_file = Path(f"logs/relatorios/relatorio_{caso}.json")
        relatorio_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"📋 Relatório salvo: {relatorio_file}")
        
        await gerenciador.finalizar()
        await monitor.finalizar()
        
        print("✅ Execução concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        logging.error(f"Erro na execução do caso {caso}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Executar caso de uso específico")
    parser.add_argument("--caso", required=True, help="Nome do caso (ex: arbitragem_alta_vol_btcusdt)")
    
    args = parser.parse_args()
    
    success = asyncio.run(executar_caso(args.caso))
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
