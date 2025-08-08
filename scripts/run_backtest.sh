#!/bin/bash

set -e

echo "📊 INICIANDO BACKTEST - CRYPTOBOT SUPREMO GLOBAL"
echo "==============================================="

if [ -d "venv" ]; then
    source venv/bin/activate
fi

export MODO=backtest
export PAPER_MODE=true

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🤖 Executando backtest para todos os bots..."

BOTS=("arbitragem" "grid" "momentum" "scalping" "mean_reversion" "swing")

for bot in "${BOTS[@]}"; do
    echo "📈 Executando backtest para bot: $bot"
    
    for caso in {1..3}; do
        echo "  📋 Caso de uso $caso..."
        
        python scripts/executar.py \
            --bot="$bot" \
            --caso="$caso" \
            --modo="backtest" \
            --output="logs/relatorios/backtest_${bot}_caso${caso}_${TIMESTAMP}.json" \
            || echo "⚠️  Falha no caso $caso do bot $bot"
    done
done

echo "📋 Gerando relatório consolidado..."
python scripts/relatorio_geral.py \
    --tipo="backtest" \
    --timestamp="$TIMESTAMP" \
    --output="logs/relatorios/RELATORIO_BACKTEST_${TIMESTAMP}.json"

echo "✅ Backtest concluído! Relatórios em logs/relatorios/"
echo "📁 Relatório principal: logs/relatorios/RELATORIO_BACKTEST_${TIMESTAMP}.json"
