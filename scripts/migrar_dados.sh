#!/bin/bash

set -e

echo "📦 MIGRAÇÃO DE DADOS - CRYPTOBOT SUPREMO GLOBAL"
echo "=============================================="

echo "📁 Criando estrutura de dados..."
mkdir -p data/{backtest,paper,live}
mkdir -p data/historical/{binance,coinbase,kraken}
mkdir -p data/cache
mkdir -p data/models

if [ -f "config.json" ] && [ ! -f "config/config.json" ]; then
    echo "📋 Migrando configuração antiga..."
    mv config.json config/config.json
fi

echo "📊 Criando índices de dados..."
cat > data/index.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "1.0.0",
    "estrutura": {
        "backtest": "Dados de backtesting histórico",
        "paper": "Dados de paper trading",
        "live": "Dados de trading ao vivo",
        "historical": "Dados históricos por exchange",
        "cache": "Cache de dados em tempo real",
        "models": "Modelos de IA treinados"
    },
    "status": "inicializado"
}
EOF

echo "✅ Migração de dados concluída"
