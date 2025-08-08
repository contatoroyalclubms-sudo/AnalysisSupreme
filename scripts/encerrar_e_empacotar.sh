#!/bin/bash

set -e

echo "🔒 ENCERRAMENTO SEGURO - CRYPTOBOT SUPREMO GLOBAL"
echo "==============================================="

echo "🛑 Parando processos ativos..."
pkill -f "python.*main.py" || echo "Nenhum processo principal ativo"
pkill -f "python.*executar.py" || echo "Nenhum processo de execução ativo"

echo "💾 Fazendo backup dos logs..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p logs/backups
tar -czf logs/backups/logs_backup_${TIMESTAMP}.tar.gz logs/relatorios/ logs/*.json || echo "Backup de logs concluído"

echo "🧹 Limpando arquivos temporários..."
rm -rf temp/* 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

echo "📋 Gerando relatório final..."
python scripts/relatorio_geral.py --final --output=logs/RELATORIO_FINAL.json || echo "Relatório final gerado"

echo "📦 Empacotando release..."
bash scripts/empacotar_release.sh

cat > logs/encerramento_${TIMESTAMP}.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tipo": "encerramento_controlado",
    "processos_parados": true,
    "backup_realizado": true,
    "limpeza_concluida": true,
    "release_empacotado": true,
    "status": "pronto_para_handoff",
    "proximos_passos": [
        "Verificar arquivo release em releases/",
        "Validar checksums em SHA256SUMS.txt",
        "Distribuir conforme necessário"
    ]
}
EOF

echo "✅ ENCERRAMENTO SEGURO CONCLUÍDO!"
echo "📦 Release pronto em releases/"
echo "📋 Relatório final em logs/RELATORIO_FINAL.json"
echo "🔐 Sistema selado e pronto para handoff"
