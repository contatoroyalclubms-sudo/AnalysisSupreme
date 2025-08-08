# 💾 PROCEDIMENTOS DE BACKUP - CRYPTOBOT SUPREMO GLOBAL

## 🎯 Visão Geral

Este documento define os procedimentos completos de backup para garantir a segurança e recuperação dos dados do sistema CRYPTOBOT SUPREMO GLOBAL.

## 📋 Estratégia de Backup

### Tipos de Backup

1. **🔄 Backup Incremental** - Diário (apenas mudanças)
2. **📦 Backup Completo** - Semanal (todos os dados)
3. **⚙️ Backup de Configuração** - Antes de mudanças
4. **🚨 Backup de Emergência** - Sob demanda

### Frequência

- **Configurações**: Antes de cada mudança
- **Dados de trading**: A cada 6 horas
- **Logs**: Diariamente
- **Sistema completo**: Semanalmente
- **Modelos de IA**: Após treinamento

## 🔧 Scripts de Backup

### 1. Backup Completo

```bash
# Executar backup completo
bash scripts/backup_completo.sh

# Com compressão
bash scripts/backup_completo.sh --compress

# Para destino específico
bash scripts/backup_completo.sh --destino=/backup/external
```

### 2. Backup Incremental

```bash
# Backup incremental diário
bash scripts/backup_incremental.sh

# Backup desde data específica
bash scripts/backup_incremental.sh --desde=2025-01-01
```

### 3. Backup de Configuração

```bash
# Backup apenas configurações
bash scripts/backup_configs.sh

# Backup com versionamento
bash scripts/backup_configs.sh --version
```

## 📁 Estrutura de Backup

```
backups/
├── completo/
│   ├── backup_completo_20250108_120000.tar.gz
│   ├── backup_completo_20250101_120000.tar.gz
│   └── ...
├── incremental/
│   ├── backup_inc_20250108_060000.tar.gz
│   ├── backup_inc_20250107_180000.tar.gz
│   └── ...
├── configuracao/
│   ├── config_backup_20250108_100000.tar.gz
│   └── ...
├── dados/
│   ├── dados_trading_20250108.tar.gz
│   └── ...
└── logs/
    ├── logs_backup_20250108.tar.gz
    └── ...
```

## 🔄 Backup Automático

### 1. Configurar Cron

```bash
# Editar crontab
crontab -e

# Adicionar tarefas de backup
# Backup incremental a cada 6 horas
0 */6 * * * cd /path/to/AnalysisSupreme && bash scripts/backup_incremental.sh

# Backup completo semanal (domingo 2h)
0 2 * * 0 cd /path/to/AnalysisSupreme && bash scripts/backup_completo.sh

# Limpeza de backups antigos (mensal)
0 3 1 * * cd /path/to/AnalysisSupreme && bash scripts/cleanup_old_backups.sh
```

### 2. Systemd Timer (Alternativa)

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/cryptobot-backup.service

[Unit]
Description=CryptoBot Backup Service
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/AnalysisSupreme
ExecStart=/bin/bash scripts/backup_incremental.sh

# Criar timer
sudo nano /etc/systemd/system/cryptobot-backup.timer

[Unit]
Description=CryptoBot Backup Timer
Requires=cryptobot-backup.service

[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target

# Ativar timer
sudo systemctl enable cryptobot-backup.timer
sudo systemctl start cryptobot-backup.timer
```

## 💾 Backup Local

### Script de Backup Completo

```bash
#!/bin/bash
# scripts/backup_completo.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/completo"
BACKUP_NAME="backup_completo_${TIMESTAMP}"

echo "🔄 Iniciando backup completo..."

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Criar backup
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='backups' \
    --exclude='temp' \
    .

# Gerar checksum
cd $BACKUP_DIR
sha256sum "${BACKUP_NAME}.tar.gz" > "${BACKUP_NAME}.sha256"
cd -

# Criar metadados
cat > "${BACKUP_DIR}/${BACKUP_NAME}.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tipo": "completo",
    "arquivo": "${BACKUP_NAME}.tar.gz",
    "tamanho_mb": $(du -m "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1),
    "checksum": "$(cat "${BACKUP_DIR}/${BACKUP_NAME}.sha256" | cut -d' ' -f1)",
    "versao_sistema": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "conteudo": [
        "codigo_fonte",
        "configuracoes",
        "dados_trading",
        "logs",
        "modelos_ia",
        "scripts"
    ]
}
EOF

echo "✅ Backup completo criado: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 Tamanho: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
```

### Script de Backup Incremental

```bash
#!/bin/bash
# scripts/backup_incremental.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/incremental"
BACKUP_NAME="backup_inc_${TIMESTAMP}"
LAST_BACKUP_FILE="backups/.last_backup"

echo "🔄 Iniciando backup incremental..."

# Determinar data do último backup
if [ -f "$LAST_BACKUP_FILE" ]; then
    LAST_BACKUP=$(cat $LAST_BACKUP_FILE)
    echo "📅 Último backup: $LAST_BACKUP"
else
    LAST_BACKUP=$(date -d "1 day ago" +%Y-%m-%d)
    echo "📅 Primeiro backup incremental, usando: $LAST_BACKUP"
fi

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Encontrar arquivos modificados
find . -type f \
    -newer "$LAST_BACKUP_FILE" \
    -not -path "./venv/*" \
    -not -path "./backups/*" \
    -not -path "./__pycache__/*" \
    -not -name "*.pyc" \
    > /tmp/files_to_backup.txt

# Criar backup incremental
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    -T /tmp/files_to_backup.txt

# Atualizar timestamp do último backup
echo $(date +%Y-%m-%d) > $LAST_BACKUP_FILE

# Gerar metadados
cat > "${BACKUP_DIR}/${BACKUP_NAME}.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "tipo": "incremental",
    "arquivo": "${BACKUP_NAME}.tar.gz",
    "ultimo_backup": "$LAST_BACKUP",
    "arquivos_modificados": $(wc -l < /tmp/files_to_backup.txt),
    "tamanho_mb": $(du -m "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
}
EOF

echo "✅ Backup incremental criado: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📁 Arquivos incluídos: $(wc -l < /tmp/files_to_backup.txt)"

# Limpeza
rm /tmp/files_to_backup.txt
```

## ☁️ Backup Remoto

### 1. AWS S3

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciais
aws configure

# Script de upload para S3
#!/bin/bash
# scripts/backup_to_s3.sh

BUCKET_NAME="cryptobot-backups"
LOCAL_BACKUP_DIR="backups"

# Sincronizar com S3
aws s3 sync $LOCAL_BACKUP_DIR s3://$BUCKET_NAME/$(hostname)/ \
    --exclude "*.tmp" \
    --storage-class STANDARD_IA

echo "✅ Backup sincronizado com S3"
```

### 2. Google Drive

```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar Google Drive
rclone config

# Script de upload
#!/bin/bash
# scripts/backup_to_gdrive.sh

rclone sync backups/ gdrive:CryptoBot-Backups/ \
    --progress \
    --exclude "*.tmp"

echo "✅ Backup sincronizado com Google Drive"
```

### 3. Servidor Remoto (rsync)

```bash
#!/bin/bash
# scripts/backup_to_remote.sh

REMOTE_HOST="backup-server.com"
REMOTE_USER="backup"
REMOTE_PATH="/backups/cryptobot"

# Sincronizar via rsync
rsync -avz --delete \
    --exclude 'venv' \
    --exclude '__pycache__' \
    backups/ \
    $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

echo "✅ Backup sincronizado com servidor remoto"
```

## 🔐 Backup Criptografado

### 1. GPG Encryption

```bash
#!/bin/bash
# scripts/backup_encrypted.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_encrypted_${TIMESTAMP}"
GPG_RECIPIENT="backup@cryptobot.com"

# Criar backup e criptografar
tar -czf - \
    --exclude='venv' \
    --exclude='backups' \
    . | gpg --encrypt --recipient $GPG_RECIPIENT \
    > "backups/${BACKUP_NAME}.tar.gz.gpg"

echo "✅ Backup criptografado criado"
```

### 2. OpenSSL Encryption

```bash
#!/bin/bash
# scripts/backup_ssl_encrypted.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_ssl_${TIMESTAMP}"
PASSWORD_FILE="backups/.backup_password"

# Gerar senha se não existir
if [ ! -f "$PASSWORD_FILE" ]; then
    openssl rand -base64 32 > $PASSWORD_FILE
    chmod 600 $PASSWORD_FILE
fi

# Criar backup criptografado
tar -czf - \
    --exclude='venv' \
    --exclude='backups' \
    . | openssl enc -aes-256-cbc \
    -pass file:$PASSWORD_FILE \
    > "backups/${BACKUP_NAME}.tar.gz.enc"

echo "✅ Backup criptografado com OpenSSL criado"
```

## 📊 Monitoramento de Backup

### 1. Verificação de Integridade

```bash
#!/bin/bash
# scripts/verify_backups.sh

echo "🔍 Verificando integridade dos backups..."

for backup in backups/completo/*.tar.gz; do
    if [ -f "${backup}.sha256" ]; then
        echo "Verificando: $(basename $backup)"
        if sha256sum -c "${backup}.sha256" --quiet; then
            echo "✅ OK"
        else
            echo "❌ CORROMPIDO: $backup"
        fi
    fi
done
```

### 2. Relatório de Backup

```bash
#!/bin/bash
# scripts/backup_report.sh

echo "📊 RELATÓRIO DE BACKUP - $(date)"
echo "================================"

# Estatísticas gerais
echo "📁 Backups completos: $(ls backups/completo/*.tar.gz 2>/dev/null | wc -l)"
echo "📁 Backups incrementais: $(ls backups/incremental/*.tar.gz 2>/dev/null | wc -l)"
echo "💾 Espaço total usado: $(du -sh backups/ | cut -f1)"

# Último backup
LAST_BACKUP=$(ls -t backups/completo/*.tar.gz 2>/dev/null | head -1)
if [ -n "$LAST_BACKUP" ]; then
    echo "🕐 Último backup completo: $(basename $LAST_BACKUP)"
    echo "📊 Tamanho: $(du -h "$LAST_BACKUP" | cut -f1)"
fi

# Verificar espaço em disco
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  AVISO: Uso de disco alto ($DISK_USAGE%)"
fi
```

## 🧹 Limpeza de Backups

### 1. Política de Retenção

```bash
#!/bin/bash
# scripts/cleanup_old_backups.sh

echo "🧹 Limpando backups antigos..."

# Manter apenas os últimos 7 backups completos
cd backups/completo
ls -t *.tar.gz | tail -n +8 | xargs rm -f
ls -t *.json | tail -n +8 | xargs rm -f
ls -t *.sha256 | tail -n +8 | xargs rm -f

# Manter backups incrementais por 30 dias
find ../incremental/ -name "*.tar.gz" -mtime +30 -delete
find ../incremental/ -name "*.json" -mtime +30 -delete

echo "✅ Limpeza concluída"
```

### 2. Compressão de Backups Antigos

```bash
#!/bin/bash
# scripts/compress_old_backups.sh

# Compactar backups com mais de 7 dias
find backups/ -name "*.tar.gz" -mtime +7 -exec gzip {} \;

echo "✅ Backups antigos compactados"
```

## 🚨 Backup de Emergência

### Script de Emergência

```bash
#!/bin/bash
# scripts/emergency_backup.sh

echo "🚨 BACKUP DE EMERGÊNCIA INICIADO"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EMERGENCY_DIR="backups/emergency"
mkdir -p $EMERGENCY_DIR

# Backup crítico (apenas essencial)
tar -czf "${EMERGENCY_DIR}/emergency_${TIMESTAMP}.tar.gz" \
    config/ \
    .env \
    logs/RELATORIO_FINAL.json \
    data/live/ \
    src/

echo "✅ Backup de emergência criado"
echo "📁 Local: ${EMERGENCY_DIR}/emergency_${TIMESTAMP}.tar.gz"
```

## 📋 Checklist de Backup

### Diário
- [ ] Verificar execução do backup incremental
- [ ] Verificar espaço em disco
- [ ] Verificar logs de backup

### Semanal
- [ ] Executar backup completo
- [ ] Verificar integridade dos backups
- [ ] Testar restauração de um backup
- [ ] Sincronizar com backup remoto

### Mensal
- [ ] Limpeza de backups antigos
- [ ] Atualizar política de retenção
- [ ] Revisar estratégia de backup
- [ ] Documentar mudanças

## 🔧 Configuração de Alertas

```bash
# Alerta se backup falhar
if ! bash scripts/backup_incremental.sh; then
    echo "❌ Backup falhou em $(date)" | \
    mail -s "FALHA DE BACKUP - CryptoBot" admin@empresa.com
fi

# Alerta se espaço em disco baixo
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️ Espaço em disco crítico: $DISK_USAGE%" | \
    mail -s "ESPAÇO EM DISCO CRÍTICO" admin@empresa.com
fi
```

---

**💾 Backup = Segurança = Tranquilidade**

Próximo: [Procedimentos de Rollback](ROLLBACK.md)
