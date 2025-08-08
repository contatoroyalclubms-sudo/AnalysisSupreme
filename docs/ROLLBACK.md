# 🔄 PROCEDIMENTOS DE ROLLBACK - CRYPTOBOT SUPREMO GLOBAL

## 🎯 Visão Geral

Este documento define os procedimentos completos de rollback para reverter o sistema CRYPTOBOT SUPREMO GLOBAL para um estado anterior estável em caso de problemas.

## 🚨 Quando Fazer Rollback

### Situações Críticas
- **💥 Falha total do sistema**
- **📉 Perdas significativas não esperadas**
- **🔧 Atualização com bugs críticos**
- **🔒 Comprometimento de segurança**
- **⚡ Performance degradada severamente**

### Indicadores de Alerta
- **Erro rate > 50%**
- **Latência > 5x normal**
- **Perda > limite configurado**
- **Falha de conectividade persistente**
- **Corrupção de dados**

## 🔄 Tipos de Rollback

### 1. Rollback de Código
```bash
# Reverter para commit anterior
git reset --hard HEAD~1

# Reverter para tag específica
git reset --hard v1.0.0

# Reverter arquivo específico
git checkout HEAD~1 -- src/bots/arbitragem.py
```

### 2. Rollback de Configuração
```bash
# Restaurar configuração anterior
bash scripts/rollback_config.sh

# Restaurar configuração específica
bash scripts/rollback_config.sh --arquivo=config.json --versao=20250107
```

### 3. Rollback de Dados
```bash
# Restaurar dados de backup
bash scripts/restore_backup.sh backups/completo/backup_20250107.tar.gz

# Restaurar apenas dados de trading
bash scripts/restore_trading_data.sh backups/dados/dados_20250107.tar.gz
```

### 4. Rollback Completo
```bash
# Rollback completo do sistema
bash scripts/rollback_completo.sh --versao=20250107
```

## 🛠️ Scripts de Rollback

### 1. Rollback Automático

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

echo "🔄 INICIANDO ROLLBACK AUTOMÁTICO"
echo "==============================="

# Verificar se há backup disponível
LAST_BACKUP=$(ls -t backups/completo/*.tar.gz 2>/dev/null | head -1)
if [ -z "$LAST_BACKUP" ]; then
    echo "❌ Nenhum backup encontrado para rollback"
    exit 1
fi

echo "📦 Usando backup: $(basename $LAST_BACKUP)"

# Parar sistema
echo "🛑 Parando sistema..."
bash scripts/emergency_stop.sh

# Fazer backup do estado atual (para possível rollforward)
echo "💾 Fazendo backup do estado atual..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/pre_rollback_${TIMESTAMP}.tar.gz" \
    --exclude='venv' \
    --exclude='backups' \
    .

# Restaurar backup
echo "🔄 Restaurando backup..."
tar -xzf "$LAST_BACKUP" --overwrite

# Reconfigurar ambiente
echo "⚙️ Reconfigurando ambiente..."
source venv/bin/activate
pip install -r requirements.txt

# Verificar integridade
echo "🔍 Verificando integridade..."
python scripts/verify_integrity.py

# Reiniciar sistema
echo "🚀 Reiniciando sistema..."
bash scripts/start_system.sh

echo "✅ ROLLBACK CONCLUÍDO COM SUCESSO"
```

### 2. Rollback de Configuração

```bash
#!/bin/bash
# scripts/rollback_config.sh

VERSAO=${1:-"ultima"}
CONFIG_BACKUP_DIR="backups/configuracao"

echo "🔄 Rollback de configuração para versão: $VERSAO"

if [ "$VERSAO" = "ultima" ]; then
    BACKUP_FILE=$(ls -t $CONFIG_BACKUP_DIR/*.tar.gz | head -1)
else
    BACKUP_FILE=$(ls $CONFIG_BACKUP_DIR/*${VERSAO}*.tar.gz | head -1)
fi

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Backup de configuração não encontrado"
    exit 1
fi

# Backup da configuração atual
cp -r config/ config_backup_$(date +%Y%m%d_%H%M%S)/

# Restaurar configuração
tar -xzf "$BACKUP_FILE" config/

echo "✅ Configuração restaurada de: $(basename $BACKUP_FILE)"
```

### 3. Rollback Seletivo

```bash
#!/bin/bash
# scripts/rollback_seletivo.sh

COMPONENTE=$1
VERSAO=$2

case $COMPONENTE in
    "bots")
        echo "🤖 Rollback dos bots..."
        git checkout $VERSAO -- src/bots/
        ;;
    "ia")
        echo "🧠 Rollback do sistema de IA..."
        git checkout $VERSAO -- src/ia/
        ;;
    "config")
        echo "⚙️ Rollback de configuração..."
        bash scripts/rollback_config.sh $VERSAO
        ;;
    "dados")
        echo "💾 Rollback de dados..."
        bash scripts/restore_trading_data.sh $VERSAO
        ;;
    *)
        echo "❌ Componente inválido: $COMPONENTE"
        echo "Componentes disponíveis: bots, ia, config, dados"
        exit 1
        ;;
esac

echo "✅ Rollback de $COMPONENTE concluído"
```

## 🔍 Verificação Pós-Rollback

### 1. Checklist de Verificação

```bash
#!/bin/bash
# scripts/verify_rollback.sh

echo "🔍 VERIFICAÇÃO PÓS-ROLLBACK"
echo "=========================="

# Verificar serviços
echo "📊 Verificando serviços..."
python scripts/health_check.py

# Verificar configuração
echo "⚙️ Verificando configuração..."
python scripts/validate_config.py

# Verificar conectividade
echo "🌐 Verificando conectividade..."
python scripts/test_exchanges.py

# Verificar dados
echo "💾 Verificando integridade dos dados..."
python scripts/verify_data_integrity.py

# Teste básico de funcionalidade
echo "🧪 Executando testes básicos..."
pytest tests/test_basic_functionality.py -v

echo "✅ Verificação concluída"
```

### 2. Teste de Smoke

```bash
#!/bin/bash
# scripts/smoke_test_rollback.sh

echo "💨 SMOKE TEST PÓS-ROLLBACK"
echo "========================="

# Testar cada bot por 30 segundos
BOTS=("arbitragem" "grid" "momentum" "scalping" "mean_reversion" "swing")

for bot in "${BOTS[@]}"; do
    echo "🤖 Testando bot: $bot"
    
    timeout 30s python scripts/executar.py \
        --bot=$bot \
        --caso=1 \
        --modo=paper \
        --duracao=30 || echo "⚠️ Teste de $bot com timeout"
done

echo "✅ Smoke test concluído"
```

## 📊 Monitoramento Pós-Rollback

### 1. Métricas de Recuperação

```bash
#!/bin/bash
# scripts/monitor_recovery.sh

echo "📊 MONITORAMENTO DE RECUPERAÇÃO"
echo "=============================="

# Monitorar por 1 hora após rollback
END_TIME=$(($(date +%s) + 3600))

while [ $(date +%s) -lt $END_TIME ]; do
    # Verificar performance
    LATENCY=$(python scripts/check_latency.py)
    ERROR_RATE=$(python scripts/check_error_rate.py)
    
    echo "$(date): Latência: ${LATENCY}ms, Erro: ${ERROR_RATE}%"
    
    # Alertar se métricas ruins
    if (( $(echo "$LATENCY > 100" | bc -l) )); then
        echo "⚠️ ALERTA: Latência alta ($LATENCY ms)"
    fi
    
    if (( $(echo "$ERROR_RATE > 5" | bc -l) )); then
        echo "⚠️ ALERTA: Taxa de erro alta ($ERROR_RATE%)"
    fi
    
    sleep 60
done

echo "✅ Monitoramento de recuperação concluído"
```

### 2. Relatório de Rollback

```bash
#!/bin/bash
# scripts/rollback_report.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="logs/rollback_report_${TIMESTAMP}.json"

cat > $REPORT_FILE << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tipo": "rollback_report",
    "versao_anterior": "$(git log --oneline -1 HEAD~1)",
    "versao_atual": "$(git log --oneline -1)",
    "backup_usado": "$(ls -t backups/completo/*.tar.gz | head -1 | xargs basename)",
    "duracao_rollback_minutos": 0,
    "verificacoes": {
        "health_check": "$(python scripts/health_check.py --json | jq -r '.status')",
        "config_valida": "$(python scripts/validate_config.py --json | jq -r '.valid')",
        "conectividade": "$(python scripts/test_exchanges.py --json | jq -r '.all_connected')"
    },
    "metricas_pos_rollback": {
        "latencia_media_ms": $(python scripts/check_latency.py --json | jq -r '.average'),
        "taxa_erro_percent": $(python scripts/check_error_rate.py --json | jq -r '.rate'),
        "bots_ativos": $(python scripts/count_active_bots.py)
    },
    "status": "concluido"
}
EOF

echo "📋 Relatório de rollback gerado: $REPORT_FILE"
```

## 🚨 Rollback de Emergência

### 1. Procedimento de Emergência

```bash
#!/bin/bash
# scripts/emergency_rollback.sh

echo "🚨 ROLLBACK DE EMERGÊNCIA INICIADO"
echo "================================="

# Parar TUDO imediatamente
pkill -f "python.*main.py" || true
pkill -f "python.*executar.py" || true

# Fechar todas as posições abertas
python scripts/emergency_close_positions.py --force

# Rollback para último backup conhecido bom
EMERGENCY_BACKUP="backups/emergency/last_known_good.tar.gz"

if [ -f "$EMERGENCY_BACKUP" ]; then
    echo "📦 Restaurando backup de emergência..."
    tar -xzf "$EMERGENCY_BACKUP" --overwrite
else
    echo "❌ Backup de emergência não encontrado!"
    echo "🔄 Usando último backup completo..."
    LAST_BACKUP=$(ls -t backups/completo/*.tar.gz | head -1)
    tar -xzf "$LAST_BACKUP" --overwrite
fi

# Configurar modo seguro
export MODO=paper
export PAPER_MODE=true
export EMERGENCY_MODE=true

echo "✅ ROLLBACK DE EMERGÊNCIA CONCLUÍDO"
echo "⚠️ SISTEMA EM MODO SEGURO (PAPER ONLY)"
```

### 2. Modo de Recuperação

```bash
#!/bin/bash
# scripts/recovery_mode.sh

echo "🔧 INICIANDO MODO DE RECUPERAÇÃO"
echo "==============================="

# Configurar variáveis de ambiente seguras
export MODO=recovery
export PAPER_MODE=true
export MAX_POSITION_SIZE=0.001
export STOP_LOSS_GLOBAL=0.01

# Desabilitar bots de alto risco
python scripts/disable_high_risk_bots.py

# Executar apenas bots conservadores
python scripts/enable_conservative_bots.py

# Monitoramento intensivo
python scripts/intensive_monitoring.py &

echo "✅ Modo de recuperação ativado"
echo "📊 Monitoramento intensivo iniciado"
```

## 📋 Plano de Rollback por Cenário

### Cenário 1: Atualização com Bug

```bash
# 1. Identificar problema
python scripts/diagnose_issue.py

# 2. Rollback de código
git reset --hard HEAD~1

# 3. Reinstalar dependências
pip install -r requirements.txt

# 4. Verificar funcionamento
bash scripts/smoke_test.sh
```

### Cenário 2: Corrupção de Dados

```bash
# 1. Parar sistema
bash scripts/emergency_stop.sh

# 2. Restaurar dados do backup
bash scripts/restore_trading_data.sh

# 3. Verificar integridade
python scripts/verify_data_integrity.py

# 4. Reiniciar gradualmente
bash scripts/gradual_restart.sh
```

### Cenário 3: Falha de Configuração

```bash
# 1. Backup configuração atual
cp -r config/ config_backup_$(date +%Y%m%d_%H%M%S)/

# 2. Restaurar configuração anterior
bash scripts/rollback_config.sh

# 3. Validar configuração
python scripts/validate_config.py

# 4. Reiniciar serviços
bash scripts/restart_services.sh
```

### Cenário 4: Comprometimento de Segurança

```bash
# 1. Isolamento imediato
bash scripts/security_isolation.sh

# 2. Rollback completo
bash scripts/rollback_completo.sh

# 3. Rotacionar chaves API
python scripts/rotate_all_api_keys.py

# 4. Auditoria de segurança
python scripts/security_audit.py
```

## 🔄 Rollforward (Reverter Rollback)

### Quando Rollforward é Necessário

```bash
#!/bin/bash
# scripts/rollforward.sh

echo "🔄 INICIANDO ROLLFORWARD"
echo "======================="

# Verificar se há backup pré-rollback
PRE_ROLLBACK=$(ls -t backups/pre_rollback_*.tar.gz 2>/dev/null | head -1)

if [ -z "$PRE_ROLLBACK" ]; then
    echo "❌ Backup pré-rollback não encontrado"
    exit 1
fi

echo "📦 Restaurando estado pré-rollback: $(basename $PRE_ROLLBACK)"

# Fazer backup do estado atual
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/pre_rollforward_${TIMESTAMP}.tar.gz" \
    --exclude='venv' \
    --exclude='backups' \
    .

# Restaurar estado pré-rollback
tar -xzf "$PRE_ROLLBACK" --overwrite

echo "✅ ROLLFORWARD CONCLUÍDO"
```

## 📊 Métricas de Rollback

### Dashboard de Rollback

```python
# scripts/rollback_dashboard.py

import json
from datetime import datetime, timedelta

def generate_rollback_metrics():
    """Gera métricas de rollback"""
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "rollbacks_ultimos_30_dias": count_recent_rollbacks(),
        "tempo_medio_rollback_minutos": calculate_average_rollback_time(),
        "taxa_sucesso_rollback": calculate_rollback_success_rate(),
        "componentes_mais_rollback": get_most_rolled_back_components(),
        "backup_mais_usado": get_most_used_backup()
    }
    
    return metrics

def count_recent_rollbacks():
    """Conta rollbacks dos últimos 30 dias"""
    # Implementação...
    return 3

def calculate_average_rollback_time():
    """Calcula tempo médio de rollback"""
    # Implementação...
    return 15.5

if __name__ == "__main__":
    metrics = generate_rollback_metrics()
    print(json.dumps(metrics, indent=2))
```

## 📋 Checklist de Rollback

### Pré-Rollback
- [ ] Identificar causa raiz do problema
- [ ] Verificar disponibilidade de backup
- [ ] Notificar stakeholders
- [ ] Documentar estado atual
- [ ] Fazer backup pré-rollback

### Durante Rollback
- [ ] Parar sistema gradualmente
- [ ] Fechar posições abertas
- [ ] Executar rollback
- [ ] Verificar integridade
- [ ] Testar funcionalidades básicas

### Pós-Rollback
- [ ] Monitorar métricas
- [ ] Executar smoke tests
- [ ] Verificar logs
- [ ] Gerar relatório
- [ ] Planejar correção definitiva

## 🚨 Contatos de Emergência

```bash
# Notificação automática em caso de rollback
#!/bin/bash
# scripts/notify_rollback.sh

ROLLBACK_TYPE=$1
REASON=$2

# Telegram
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    -d text="🚨 ROLLBACK EXECUTADO
Tipo: $ROLLBACK_TYPE
Motivo: $REASON
Timestamp: $(date)
Sistema: $(hostname)"

# Email
echo "ROLLBACK executado no sistema CryptoBot
Tipo: $ROLLBACK_TYPE
Motivo: $REASON
Timestamp: $(date)" | \
mail -s "🚨 ROLLBACK EXECUTADO - CryptoBot" admin@empresa.com
```

---

**🔄 Rollback Rápido = Recuperação Rápida = Negócio Protegido**

Próximo: [Histórico de Mudanças](CHANGELOG.md)
