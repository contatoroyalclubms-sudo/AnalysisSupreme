#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "🚀 INSTALADOR UNIVERSAL - CRYPTOBOT SUPREMO GLOBAL"
echo "=================================================="
echo -e "${NC}"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERRO: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] AVISO: $1${NC}"
}

if [ ! -f "requirements.txt" ] || [ ! -f "main.py" ]; then
    error "Execute este script no diretório raiz do projeto AnalysisSupreme"
    exit 1
fi

log "Executando pré-checagens do sistema..."
if [ -f "scripts/pre_checks.sh" ]; then
    chmod +x scripts/pre_checks.sh
    if ! bash scripts/pre_checks.sh; then
        error "Pré-checagens falharam. Corrija os problemas antes de continuar."
        exit 1
    fi
else
    warning "Arquivo de pré-checagens não encontrado, continuando..."
fi

log "Criando estrutura de diretórios..."
mkdir -p logs/{relatorios,benchmarks,backups}
mkdir -p data/{backtest,paper,live}
mkdir -p config/environments
mkdir -p releases
mkdir -p temp

log "Configurando ambiente Python..."
if ! command -v python3 &> /dev/null; then
    error "Python3 não encontrado. Instale Python 3.9+ antes de continuar."
    exit 1
fi

if [ ! -d "venv" ]; then
    log "Criando ambiente virtual..."
    python3 -m venv venv
else
    log "Ambiente virtual já existe"
fi

log "Ativando ambiente virtual..."
source venv/bin/activate

log "Atualizando pip..."
pip install --upgrade pip

log "Instalando dependências Python..."
pip install -r requirements.txt

if [ -f "requirements-dev.txt" ]; then
    log "Instalando dependências de desenvolvimento..."
    pip install -r requirements-dev.txt
fi

log "Configurando arquivo de ambiente..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log "Arquivo .env criado a partir do .env.example"
        warning "IMPORTANTE: Configure suas chaves API no arquivo .env antes de usar"
    elif [ -f "configuracoes/.env.example" ]; then
        cp configuracoes/.env.example .env
        log "Arquivo .env criado a partir do configuracoes/.env.example"
        warning "IMPORTANTE: Configure suas chaves API no arquivo .env antes de usar"
    else
        warning "Arquivo .env.example não encontrado, criando .env básico..."
        cat > .env << EOF
MODO=paper
LOG_LEVEL=INFO
PAPER_MODE=true

BINANCE_API_KEY=sua_chave_aqui
BINANCE_SECRET_KEY=sua_chave_secreta_aqui
COINBASE_API_KEY=sua_chave_aqui
COINBASE_SECRET_KEY=sua_chave_secreta_aqui

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

MAX_CONCURRENT_TRADES=50
EXECUTION_TIMEOUT_MS=15000
WEBSOCKET_TIMEOUT_MS=1000
EOF
    fi
else
    log "Arquivo .env já existe"
fi

log "Configurando arquivo de configuração principal..."
if [ ! -f "config/config.json" ]; then
    if [ -f "config/config.example.json" ]; then
        cp config/config.example.json config/config.json
        log "Arquivo config.json criado a partir do config.example.json"
    else
        warning "Arquivo config.example.json não encontrado"
    fi
fi

if [ -f "scripts/migrar_dados.sh" ]; then
    log "Executando migrações de dados..."
    chmod +x scripts/migrar_dados.sh
    bash scripts/migrar_dados.sh
fi

if [ -f "scripts/seed_inicial.sh" ]; then
    log "Executando seed inicial..."
    chmod +x scripts/seed_inicial.sh
    bash scripts/seed_inicial.sh
fi

log "Configurando permissões dos scripts..."
find scripts/ -name "*.sh" -exec chmod +x {} \;
find scripts/ -name "*.py" -exec chmod +x {} \;

log "Verificando instalação..."
if python -c "import src; print('✅ Módulo src importado com sucesso')" 2>/dev/null; then
    log "Módulos Python carregados corretamente"
else
    warning "Problemas na importação dos módulos Python"
fi

log "Executando testes básicos de instalação..."
if command -v pytest &> /dev/null; then
    if pytest tests/test_simple_coverage.py -v --tb=short 2>/dev/null; then
        log "Testes básicos passaram"
    else
        warning "Alguns testes básicos falharam, mas instalação continua"
    fi
else
    warning "pytest não encontrado, pulando testes"
fi

if command -v docker &> /dev/null; then
    log "Docker encontrado, configurando containers opcionais..."
    if [ -f "docker-compose.yml" ]; then
        log "Arquivo docker-compose.yml encontrado"
        docker-compose config > /dev/null && log "docker-compose.yml válido"
    fi
else
    warning "Docker não encontrado, pulando configuração de containers"
fi

cat > logs/instalacao_status.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "versao_instalador": "1.0.0",
    "status": "concluida",
    "python_version": "$(python --version)",
    "pip_version": "$(pip --version)",
    "diretorio_instalacao": "$(pwd)",
    "usuario": "$(whoami)",
    "sistema": "$(uname -a)",
    "dependencias_instaladas": true,
    "ambiente_configurado": true,
    "scripts_executaveis": true,
    "proximos_passos": [
        "Configure suas chaves API no arquivo .env",
        "Execute 'bash scripts/run_paper.sh' para testar",
        "Execute 'make test' para validar instalação"
    ]
}
EOF

echo -e "${GREEN}"
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo -e "${NC}"

echo "📋 PRÓXIMOS PASSOS:"
echo "1. Configure suas chaves API no arquivo .env"
echo "2. Execute: source venv/bin/activate"
echo "3. Execute: bash scripts/run_paper.sh"
echo "4. Execute: make test"

echo -e "\n📁 ARQUIVOS IMPORTANTES:"
echo "- .env (configuração de ambiente)"
echo "- config/config.json (configuração principal)"
echo "- logs/instalacao_status.json (status da instalação)"

echo -e "\n🚀 COMANDOS ÚTEIS:"
echo "- make setup          # Setup completo"
echo "- make test           # Executar testes"
echo "- make run-paper      # Paper trading"
echo "- make relatorio      # Gerar relatórios"

echo -e "\n${GREEN}✅ Sistema CRYPTOBOT SUPREMO GLOBAL pronto para uso!${NC}"
