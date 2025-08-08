# 📦 GUIA DE INSTALAÇÃO - CRYPTOBOT SUPREMO GLOBAL

## 🎯 Visão Geral

Este guia fornece instruções detalhadas para instalação do sistema CRYPTOBOT SUPREMO GLOBAL em diferentes ambientes.

## 🔧 Pré-requisitos

### Sistema Operacional
- **Linux** (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **macOS** (10.15+)
- **Windows** (WSL2 recomendado)

### Software Necessário
- **Python 3.9+** (obrigatório)
- **Git** (obrigatório)
- **Docker** (opcional)
- **Redis** (opcional, para cache)

### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disco**: 2GB livres
- **Rede**: Conexão estável com internet

## 🚀 Instalação Automática (Recomendada)

### 1. Download do Projeto

```bash
# Clonar repositório
git clone https://github.com/contatoroyalclubms-sudo/AnalysisSupreme.git
cd AnalysisSupreme

# Ou baixar release
wget https://github.com/contatoroyalclubms-sudo/AnalysisSupreme/releases/latest/download/release.zip
unzip release.zip
cd cryptobot-supremo-global-*
```

### 2. Executar Instalador Universal

```bash
# Tornar executável
chmod +x installer.sh

# Executar instalação
bash installer.sh
```

O instalador irá:
- ✅ Verificar pré-requisitos
- ✅ Criar ambiente virtual Python
- ✅ Instalar dependências
- ✅ Configurar arquivos .env
- ✅ Executar migrações
- ✅ Validar instalação

### 3. Configurar Chaves API

```bash
# Editar arquivo de configuração
nano .env

# Configurar chaves das exchanges
BINANCE_API_KEY=sua_chave_binance
BINANCE_SECRET_KEY=sua_chave_secreta_binance
COINBASE_API_KEY=sua_chave_coinbase
COINBASE_SECRET_KEY=sua_chave_secreta_coinbase
```

### 4. Validar Instalação

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar testes
make test

# Testar paper trading
bash scripts/run_paper.sh
```

## 🔧 Instalação Manual

### 1. Preparar Ambiente Python

```bash
# Verificar versão Python
python3 --version

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip
```

### 2. Instalar Dependências

```bash
# Instalar dependências principais
pip install -r requirements.txt

# Instalar dependências de desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

### 3. Configurar Estrutura

```bash
# Criar diretórios necessários
mkdir -p logs/{relatorios,benchmarks,backups}
mkdir -p data/{backtest,paper,live}
mkdir -p config/environments

# Copiar arquivo de configuração
cp .env.example .env
cp config/config.example.json config/config.json
```

### 4. Executar Migrações

```bash
# Migrar dados
bash scripts/migrar_dados.sh

# Executar seed inicial
bash scripts/seed_inicial.sh
```

## 🐳 Instalação com Docker

### 1. Usando Docker Compose

```bash
# Construir e executar
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### 2. Docker Manual

```bash
# Construir imagem
docker build -t cryptobot-supremo .

# Executar container
docker run -d \
  --name cryptobot \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  cryptobot-supremo

# Verificar logs
docker logs -f cryptobot
```

## 🔧 Configuração Avançada

### Redis (Cache)

```bash
# Instalar Redis (Ubuntu)
sudo apt update
sudo apt install redis-server

# Iniciar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configurar no .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### PostgreSQL (Opcional)

```bash
# Instalar PostgreSQL (Ubuntu)
sudo apt install postgresql postgresql-contrib

# Criar banco de dados
sudo -u postgres createdb cryptobot

# Configurar no .env
DATABASE_URL=postgresql://user:password@localhost/cryptobot
```

### Nginx (Proxy Reverso)

```bash
# Instalar Nginx
sudo apt install nginx

# Configurar proxy
sudo nano /etc/nginx/sites-available/cryptobot

# Conteúdo do arquivo:
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Ativar site
sudo ln -s /etc/nginx/sites-available/cryptobot /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 🔒 Configuração de Segurança

### 1. Chaves API

```bash
# Criar arquivo de chaves seguro
touch .env
chmod 600 .env

# Nunca commitar chaves
echo ".env" >> .gitignore
```

### 2. Firewall

```bash
# Configurar UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 3. SSL/TLS (Produção)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com
```

## 📊 Verificação da Instalação

### 1. Testes Básicos

```bash
# Verificar importações
python -c "import src; print('✅ Módulos carregados')"

# Verificar configuração
python -c "from src.core.configuracao import Configuracao; print('✅ Configuração OK')"

# Verificar conexões
python scripts/test_connections.py
```

### 2. Testes Completos

```bash
# Executar suite de testes
pytest tests/ -v

# Verificar cobertura
pytest --cov=src --cov-report=html

# Testes de performance
pytest tests/performance/ --benchmark-only
```

### 3. Smoke Tests

```bash
# Teste rápido de cada bot
python scripts/smoke_test.py

# Teste de conectividade
python scripts/test_exchanges.py

# Teste de IA
python scripts/test_ai_components.py
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Permissão

```bash
# Solução
chmod +x installer.sh
chmod +x scripts/*.sh
```

#### 2. Python não encontrado

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### 3. Dependências faltando

```bash
# Reinstalar dependências
pip install --force-reinstall -r requirements.txt

# Limpar cache pip
pip cache purge
```

#### 4. Erro de conexão com exchange

```bash
# Verificar chaves API
grep -E "(API_KEY|SECRET)" .env

# Testar conectividade
curl -I https://api.binance.com/api/v3/ping
```

#### 5. Erro de importação

```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstalar em modo desenvolvimento
pip install -e .
```

### Logs de Debug

```bash
# Ativar debug
export LOG_LEVEL=DEBUG

# Verificar logs
tail -f logs/cryptobot.log

# Logs de instalação
cat logs/instalacao_status.json
```

## 📋 Checklist Pós-Instalação

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Chaves API configuradas
- [ ] Testes básicos passando
- [ ] Paper trading funcionando
- [ ] Logs sendo gerados
- [ ] Backup configurado

## 🔄 Atualizações

### Atualizar Sistema

```bash
# Fazer backup
bash scripts/backup_completo.sh

# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Executar migrações
bash scripts/migrar_dados.sh

# Validar atualização
make test
```

### Rollback

```bash
# Em caso de problemas
bash scripts/rollback.sh

# Ou restaurar backup
bash scripts/restore_backup.sh logs/backups/backup_YYYYMMDD.tar.gz
```

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. **Consulte logs**: `logs/instalacao_status.json`
2. **Verifique pré-requisitos**: `bash scripts/pre_checks.sh`
3. **Execute diagnóstico**: `python scripts/diagnostico.py`
4. **Consulte documentação**: `docs/`

---

**✅ Instalação concluída com sucesso!**

Próximo passo: [Manual de Operação](OPERACAO.md)
