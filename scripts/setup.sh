#!/bin/bash

set -e

echo "🔧 SETUP COMPLETO - CRYPTOBOT SUPREMO GLOBAL"
echo "==========================================="

if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "📁 Criando estrutura de diretórios..."
mkdir -p logs/{relatorios,benchmarks,backups}
mkdir -p data/{backtest,paper,live}
mkdir -p config/environments

if [ ! -f ".env" ]; then
    echo "⚙️  Configurando arquivo .env..."
    cp .env.example .env 2>/dev/null || cp configuracoes/.env.example .env
    echo "⚠️  IMPORTANTE: Configure suas chaves API no arquivo .env"
fi

echo "🧪 Executando testes básicos..."
python -m pytest tests/test_simple_coverage.py -v --tb=short || echo "⚠️  Alguns testes falharam"

echo "✅ Setup concluído com sucesso!"
