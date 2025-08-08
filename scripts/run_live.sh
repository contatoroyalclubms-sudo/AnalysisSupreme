#!/bin/bash

set -e

echo "🔴 LIVE TRADING - CRYPTOBOT SUPREMO GLOBAL"
echo "=========================================="

if [ "$1" != "--confirm" ] || [ "$2" != "EU_SOU_O_SUPREMO" ]; then
    echo "❌ ACESSO NEGADO!"
    echo "🔒 Live trading requer confirmação do SUPREMO"
    echo "💡 Uso: bash scripts/run_live.sh --confirm \"EU_SOU_O_SUPREMO\""
    echo "⚠️  ATENÇÃO: Live trading usa dinheiro real!"
    exit 1
fi

echo "🔓 Confirmação do SUPREMO recebida"
echo "⚠️  INICIANDO LIVE TRADING COM DINHEIRO REAL!"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

export MODO=live
export PAPER_MODE=false

if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado"
    exit 1
fi

if ! grep -q "BINANCE_API_KEY=sua_chave_aqui" .env; then
    echo "✅ Chaves API configuradas"
else
    echo "❌ Configure suas chaves API no arquivo .env primeiro"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚨 INICIANDO LIVE TRADING EM 10 SEGUNDOS..."
echo "🛑 Pressione Ctrl+C para cancelar"
sleep 10

echo "🔴 LIVE TRADING ATIVO!"

python main.py \
    --modo=live \
    --output="logs/relatorios/RELATORIO_LIVE_${TIMESTAMP}.json" \
    || echo "⚠️  Live trading finalizado"

echo "🔴 Live trading finalizado"
echo "📁 Relatório: logs/relatorios/RELATORIO_LIVE_${TIMESTAMP}.json"
