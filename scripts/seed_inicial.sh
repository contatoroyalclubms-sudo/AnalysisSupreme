#!/bin/bash

set -e

echo "🌱 SEED INICIAL - CRYPTOBOT SUPREMO GLOBAL"
echo "========================================="

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "📊 Criando dados de exemplo para backtest..."
python -c "
import json
import os
from datetime import datetime, timedelta

exemplo_backtest = {
    'timestamp': datetime.utcnow().isoformat(),
    'symbol': 'BTC/USDT',
    'timeframe': '1h',
    'data_inicio': (datetime.utcnow() - timedelta(days=30)).isoformat(),
    'data_fim': datetime.utcnow().isoformat(),
    'dados_exemplo': [
        {'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
         'open': 50000 + i*10, 'high': 50100 + i*10, 'low': 49900 + i*10, 'close': 50000 + i*10, 'volume': 100}
        for i in range(720)  # 30 dias de dados horários
    ]
}

os.makedirs('data/backtest', exist_ok=True)
with open('data/backtest/exemplo_btcusdt.json', 'w') as f:
    json.dump(exemplo_backtest, f, indent=2)

print('✅ Dados de exemplo criados')
"

echo "🤖 Criando configurações padrão dos bots..."
python -c "
import json
import os

bots_config = {
    'arbitragem': {
        'ativo': True,
        'min_profit_percent': 0.5,
        'max_position_size': 0.1,
        'exchanges': ['binance', 'coinbase']
    },
    'grid': {
        'ativo': True,
        'grid_levels': 10,
        'range_percent': 5.0,
        'order_size': 0.01
    },
    'momentum': {
        'ativo': True,
        'breakout_threshold': 1.02,
        'stop_loss': 0.02,
        'take_profit': 0.04
    },
    'scalping': {
        'ativo': True,
        'spread_target': 0.1,
        'quick_profit': 0.05,
        'max_hold_time': 60
    },
    'mean_reversion': {
        'ativo': True,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'mean_period': 20
    },
    'swing': {
        'ativo': True,
        'trend_period': 50,
        'swing_threshold': 0.05,
        'hold_time_min': 3600
    }
}

os.makedirs('config/bots', exist_ok=True)
for bot, config in bots_config.items():
    with open(f'config/bots/{bot}.json', 'w') as f:
        json.dump(config, f, indent=2)

print('✅ Configurações dos bots criadas')
"

cat > data/seed_status.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "1.0.0",
    "seeds_executados": [
        "dados_exemplo_backtest",
        "configuracoes_bots_padrao"
    ],
    "status": "concluido"
}
EOF

echo "✅ Seed inicial concluído"
