#!/bin/bash

set -e

echo "📝 INICIANDO PAPER TRADING - CRYPTOBOT SUPREMO GLOBAL"
echo "===================================================="

if [ -d "venv" ]; then
    source venv/bin/activate
fi

export MODO=paper
export PAPER_MODE=true

if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado. Execute installer.sh primeiro."
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🤖 Iniciando paper trading para todos os bots..."

python main.py \
    --modo=paper \
    --duracao=300 \
    --output="logs/relatorios/RELATORIO_PAPER_${TIMESTAMP}.json" \
    || echo "⚠️  Paper trading finalizado com avisos"

echo "✅ Paper trading concluído!"
echo "📁 Relatório: logs/relatorios/RELATORIO_PAPER_${TIMESTAMP}.json"
echo "📊 Execute 'make relatorio' para ver métricas detalhadas"
